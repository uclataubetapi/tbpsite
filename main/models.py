import os

from django import forms
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm

from points import *

MAJOR_CHOICES = (
    ('0', 'Aerospace Engineering'),
    ('1', 'Bioengineering'),
    ('2', 'Chemical Engineering'),
    ('3', 'Civil Engineering'),
    ('4', 'Computer Science'),
    ('5', 'Computer Science and Engineering'),
    ('6', 'Electrical Engineering'),
    ('7', 'Materials Engineering'),
    ('8', 'Mechanical Engineering'),
)
DEPT_CHOICES = (
    ('0', 'Bioengineering'),
    ('1', 'Chemical Engineering'),
    ('2', 'Civil and Environmental Engineering'),
    ('3', 'Computer Science'),
    ('4', 'Electrical Engineering'),
    ('5', 'Mechanical and Aerospace Engineering'),
    ('6', 'Materials Science and Engineering'),
)
DAY_CHOICES = (
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
)
HOUR_CHOICES = (
    ('0', '10am-12pm'),
    ('1', '11am-1pm'),
    ('2', '12pm-2pm'),
    ('3', '1pm-3pm'),
    ('4', '2pm-4pm'),
    ('5', '3pm-5pm'),
)

resume_pdf_fs = FileSystemStorage(location='/media/resumes_pdf')
resume_word_fs = FileSystemStorage(location='/media/resumes_word')
professor_interview_fs = FileSystemStorage(location='/media/professor_interviews')
community_service_fs = FileSystemStorage(location='/media/community_service_proof')


def upload_to_path(instance, filename):
    return '{}{}'.format(str(instance).replace(' ', '_'), os.path.splitext(filename)[1])


class Term(models.Model):
    QUARTER_CHOICES = (
        ('0', 'Winter'),
        ('1', 'Spring'),
        ('2', 'Summer'),
        ('3', 'Fall'),
    )
    quarter = models.CharField(max_length=1, choices=QUARTER_CHOICES)
    year = models.IntegerField()

    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-year', '-quarter']
        unique_together = ('quarter', 'year')

    def __unicode__(self):
        return '{} {}'.format(self.get_quarter_display(), self.year)


class SettingsManager(models.Manager):
    def settings(self):
        return super(SettingsManager, self).get_or_create(id=1)[0]

    def term(self):
        return self.settings().term

    def display_all_terms(self):
        return self.settings().display_all_terms

    def display_tutoring(self):
        return self.settings().display_tutoring

    def get_registration_code(self):
        return self.settings().registration_code

    def get_eligibility_list(self):
        return self.settings().eligibility_list


class Settings(models.Model):
    term = models.ForeignKey('Term', blank=True, null=True)
    display_all_terms = models.BooleanField(default=False)
    display_tutoring = models.BooleanField(default=False)
    registration_code = models.CharField(max_length=10, default='')
    eligibility_list = models.FileField(upload_to='files')
    objects = SettingsManager()

    class Meta:
        verbose_name_plural = "Settings"

    def __unicode__(self):
        return 'Settings'


class TermManager(models.Manager):
    def get_query_set(self):
        if not Settings.objects.display_all_terms():
            term = Settings.objects.term()
            if term:
                return super(TermManager, self).get_query_set().filter(term=term)
        return super(TermManager, self).get_query_set()


class House(models.Model):
    HOUSE_CHOICES = (
        ('0', 'Tau'),
        ('1', 'Beta'),
        ('2', 'Pi'),
        ('3', 'Epsilon'),
    )
    house = models.CharField(max_length=1, choices=HOUSE_CHOICES, unique=True)

    def __unicode__(self):
        return self.get_house_display()


class HousePoints(models.Model):
    house = models.ForeignKey('House')
    term = models.ForeignKey('Term')

    professor_interview_and_resume = models.CharField(max_length=1, choices=PLACE_CHOICES, default=FOURTH)
    other = models.IntegerField(default=0)

    current = TermManager()
    objects = models.Manager()

    class Meta:
        ordering = ('-term', 'house')
        unique_together = ('house', 'term')
        verbose_name_plural = "House Points"

    def __unicode__(self):
        return self.house.__unicode__()

    def social_list(self):
        from event.models import Event
        return Event.objects.select_related().filter(term=self.term)

    def member_list(self):
        return (list(Candidate.objects.select_related().filter(profile__house=self.house, term=self.term)) +
                list(ActiveMember.objects.select_related().filter(profile__house=self.house, term=self.term)))

    def professor_interview_and_resume_points(self):
        return DOCUMENT_POINTS[self.professor_interview_and_resume] * len(self.member_list())

    def points(self):
        return sum([sum(member.points() for member in self.member_list()),
                    sum(social.points(self.house) for social in self.social_list()),
                    self.professor_interview_and_resume_points(), self.other])


class Profile(models.Model):
    user = models.OneToOneField(User)

    middle_name = models.CharField(max_length=30, blank=True, verbose_name="Middle Name")
    nickname = models.CharField(max_length=30, blank=True, verbose_name="Nickname (optional)")
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    birthday = models.DateField(null=True, verbose_name="Birthday (mm/dd/yyyy)")
    phone_number = models.CharField(max_length=25, verbose_name="Phone Number (xxx-xxx-xxxx)")
    CANDIDATE = '0'
    MEMBER = '1'
    POSITION_CHOICES = (
        (CANDIDATE, 'Candidate'),
        (MEMBER, 'Member'),
    )
    position = models.CharField(max_length=1, choices=POSITION_CHOICES, default='0')
    house = models.ForeignKey('House', blank=True, null=True)
    major = models.CharField(max_length=1, choices=MAJOR_CHOICES, default='0')
    initiation_term = models.ForeignKey('Term', related_name='profile_initiation_term', default=Settings.objects.term)
    graduation_term = models.ForeignKey('Term', related_name='profile_graduation_term', blank=True, null=True)
    resume_pdf = models.FileField(upload_to=upload_to_path, storage=resume_pdf_fs,
                                  blank=True, null=True, default=None, verbose_name="Resume (PDF)")
    resume_word = models.FileField(upload_to=upload_to_path, storage=resume_word_fs,
                                   blank=True, null=True, default=None, verbose_name="Resume (word)")

    classes = models.ManyToManyField('tutoring.Class', blank=True, null=True)

    class Meta:
        ordering = ('position', 'user__last_name', 'user__first_name')

    def __unicode__(self):
        if self.nickname:
            return '%s %s' % ( self.nickname, self.user.last_name )
        name = self.user.get_full_name()
        return name if name else self.user.get_username()

    def current(self):
        if self.position == Profile.CANDIDATE:
            try:
                self.candidate.tutoring
            except Candidate.DoesNotExist:
                return False
        elif self.position == Profile.MEMBER:
            try:
                ActiveMember.objects.get(profile=self, term=Settings.objects.term())
            except ActiveMember.DoesNotExist:
                return False
        return True

    def dump(self):
        return ','.join(field for field in [self.user.first_name, self.middle_name, self.user.last_name,
                                            self.user.email,  self.nickname, self.gender,
                                            self.birthday.strftime('%x') if self.birthday else '', self.phone_number,
                                            self.get_major_display(),
                                            self.initiation_term.__unicode__() if self.initiation_term else '',
                                            self.graduation_term.__unicode__() if self.graduation_term else ''])


class Member(models.Model):
    profile = None
    term = models.ForeignKey('Term')

    tutoring = models.OneToOneField('tutoring.Tutoring', blank=True, null=True)
    completed = models.BooleanField(default=False)
    other = models.IntegerField(default=0)

    current = TermManager()
    objects = models.Manager()

    def __unicode__(self):
        return self.profile.__unicode__()

    class Meta:
        abstract = True
        ordering = ('term', 'profile__user__last_name', 'profile__user__first_name')

    def social_count(self):
        from event.models import Event
        return Event.objects.filter(attendees=self, term=self.term, event_type=0).count()

    # REQUIREMENTS
    def tutoring_complete(self):
        return self.tutoring.complete() if self.tutoring else False

    def social_complete(self):
        return self.social_count() >= MIN_SOCIALS

    def requirements(self):
        raise NotImplementedError

    def complete(self):
        return all(requirement for name, requirement in self.requirements())

    # POINTS
    def tutoring_points(self):
        return self.tutoring.points() if self.tutoring else False

    def social_points(self):
        count = self.social_count()
        if count > MIN_SOCIALS:
            return SOCIAL_POINTS * MIN_SOCIALS + EXTRA_SOCIAL_POINTS * (count - MIN_SOCIALS)
        return SOCIAL_POINTS * count

    def points(self):
        return sum((self.tutoring_points(), self.social_points(), self.other))


class Candidate(Member):
    profile = models.OneToOneField('Profile')

    SHIRT_SIZES = (
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    )
    shirt_size = models.CharField(max_length=2, default='M', choices=SHIRT_SIZES, verbose_name="T-Shirt Size")
    bent_polish = models.BooleanField(default=False)
    candidate_quiz = models.IntegerField(default=0)
    candidate_meet_and_greet = models.BooleanField(default=False)
    signature_book = models.BooleanField(default=False)
    community_service_proof = models.FileField(upload_to=upload_to_path, storage=community_service_fs, blank=True,
                                               null=True, default=None, verbose_name="Community Service Proof")
    community_service = models.IntegerField(default=0)
    initiation_fee = models.BooleanField(default=False)
    engineering_futures = models.BooleanField(default=False)
    professor_interview = models.FileField(upload_to=upload_to_path, storage=professor_interview_fs,
                                           blank=True, null=True, default=None, verbose_name="Professor Interview")

    def resume(self):
        return self.profile.resume_pdf or self.profile.resume_word

    # REQUIREMENTS
    def community_service_complete(self):
        return self.community_service >= MIN_COMMUNITY_SERVICE

    def requirements(self):
        return (
            ('Tutoring', self.tutoring_complete()),
            ('Bent Polish', self.bent_polish),
            ('Candidate Quiz', self.candidate_quiz),
            ('Signature Book', self.signature_book),
            ('Community Service', self.community_service_complete()),
            ('Initiation Fee', self.initiation_fee),
            ('Engineering Futures', self.engineering_futures),
            ('Social', self.social_complete()),
            ('Resume', self.resume()),
            ('Professor Interview', self.professor_interview),
        )

    # POINTS
    professor_interview_on_time = models.BooleanField(default=False)
    resume_on_time = models.BooleanField(default=False)
    quiz_first_try = models.BooleanField(default=False)

    def community_service_points(self):
        count = self.community_service
        if count > MIN_COMMUNITY_SERVICE:
            return (COMMUNITY_SERVICE_POINTS * MIN_COMMUNITY_SERVICE +
                    COMMUNITY_SERVICE_POINTS * (count - MIN_COMMUNITY_SERVICE))
        return COMMUNITY_SERVICE_POINTS * count

    def professor_interview_on_time_points(self):
        return ON_TIME_POINTS if self.professor_interview_on_time else 0

    def resume_on_time_points(self):
        return ON_TIME_POINTS if self.resume_on_time else 0

    def bent_polish_points(self):
        return BENT_POLISH_POINTS if self.bent_polish else 0

    def quiz_first_try_points(self):
        return QUIZ_FIRST_TRY_POINTS if self.quiz_first_try else 0

    def points(self):
        return sum((
            super(Candidate, self).points(), self.community_service_points(),
            self.professor_interview_on_time_points(), self.resume_on_time_points(), self.bent_polish_points(),
            self.quiz_first_try_points(), quiz_points(self.candidate_quiz), self.other,
        ))


class ActiveMember(Member):
    profile = models.ForeignKey('Profile')

    EMCC = '0'
    TUTORING = '1'
    COMMITTEE = '2'
    REQUIREMENT_CHOICES = (
        (EMCC, 'EMCC'),
        (TUTORING, 'Tutoring'),
        # TODO: comment as necessary
        (COMMITTEE, 'Rube Goldberg Committee'),
    )
    requirement_choice = models.CharField(max_length=1, choices=REQUIREMENT_CHOICES, default='0')
    requirement_complete = models.BooleanField(default=False)

    class Meta(Member.Meta):
        unique_together = ('profile', 'term')

    def requirement(self):
        if self.requirement_choice in (ActiveMember.EMCC, ActiveMember.COMMITTEE):
            return self.requirement_complete
        return self.tutoring.complete() if self.tutoring else False

    def requirements(self):
        return (
            (self.get_requirement_choice_display(), self.requirement()),
            ('Social', self.social_complete()),
        )


class Officer(models.Model):
    profile = models.ManyToManyField('Profile')

    position = models.CharField(max_length=30)
    rank = models.IntegerField()
    mail_alias = models.CharField(max_length=30)

    def list_profiles(self):
        return ', '.join([str(a) for a in self.profile.all()])

    def __unicode__(self):
        return self.position

    class Meta:
        ordering = ('rank',)


class Faculty(models.Model):
    name = models.CharField(max_length=40)
    dept = models.CharField(max_length=1, choices=DEPT_CHOICES)
    chapter = models.CharField(max_length=10)
    graduation = models.CharField(max_length=10)
    link = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Faculty Members"


class UserForm(ModelForm):

    def check_password(self, password):
        raise NotImplementedError

    def clean(self):
        cleaned_data = super(UserForm, self).clean()

        current_password, username, new_password, confirm_password = map(
            cleaned_data.get, ('current_password', 'username', 'new_password', 'confirm_password'))

        if any([username != self.instance.get_username(), new_password, confirm_password]) and not current_password:
            self._errors['current_password'] = self.error_class(["Current password required."])

        if current_password and not self.check_password(current_password):
            self._errors['current_password'] = self.error_class(["Incorrect password."])

        if username != self.instance.get_username() and User.objects.filter(username=username).count():
            self._errors['username'] = self.error_class(["Username has already been taken."])

        if new_password != confirm_password:
            self._errors['confirm_password'] = self.error_class(["Passwords do not match."])

        return cleaned_data


class UserAccountForm(UserForm):
    current_password = forms.CharField(widget=forms.widgets.PasswordInput, required=True, label="Current Password")
    username = forms.CharField(required=False)
    new_password = forms.CharField(widget=forms.widgets.PasswordInput, required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.widgets.PasswordInput, required=False, label="Confirm Password")

    class Meta:
        model = User
        fields = ['current_password', 'username', 'new_password', 'confirm_password']

    def check_password(self, password):
        return self.instance.check_password(password)


class RegisterForm(UserForm):
    current_password = forms.CharField(widget=forms.widgets.PasswordInput, label="Registration Code")
    username = forms.CharField()
    new_password = forms.CharField(widget=forms.widgets.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.widgets.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['current_password', 'username', 'new_password', 'confirm_password']

    def check_password(self, password):
        return password == Settings.objects.get_registration_code()


class UserPersonalForm(ModelForm):
    # TODO: change to email field
    email = forms.CharField(required=True)
    first_name = forms.CharField(required=True, label="Legal First Name")
    middle_name = forms.CharField(required=False, label="Preferred Name (if applicable)")
    last_name = forms.CharField(required=True, label="Last Name")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'middle_name', 'last_name']


class ProfileForm(ModelForm):
    birthday = forms.DateField(label="Birthday (mm/dd/yyyy)", widget=forms.DateInput)
    graduation_quarter = forms.ChoiceField(choices=Term.QUARTER_CHOICES, label="Graduation Quarter")
    graduation_year = forms.IntegerField(label="Graduation Year")

    class Meta:
        model = Profile
        fields = ['nickname', 'gender', 'birthday', 'phone_number', 'major',
                  'graduation_quarter', 'graduation_year', 'resume_pdf', 'resume_word']
        widgets = {
            'gender': forms.widgets.RadioSelect
        }


class FirstProfileForm(ModelForm):
    graduation_quarter = forms.ChoiceField(choices=Term.QUARTER_CHOICES, label="Graduation Quarter")
    graduation_year = forms.IntegerField(label="Graduation Year")

    class Meta:
        model = Profile
        fields = ['nickname', 'gender', 'birthday', 'phone_number', 'major', 'graduation_quarter', 'graduation_year']
        widgets = {
            'gender': forms.widgets.RadioSelect
        }


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.widgets.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        user = authenticate(username=cleaned_data.get('username'), password=cleaned_data.get('password'))
        if user is None:
            self._errors['password'] = self.error_class(["Incorrect password."])
        else:
            cleaned_data['user'] = user
        return cleaned_data


class CandidateForm(ModelForm):

    class Meta:
        model = Candidate
        fields = ['professor_interview', 'community_service_proof']


class MemberForm(ModelForm):

    class Meta:
        model = ActiveMember
        fields = ['requirement_choice']


class ShirtForm(ModelForm):

    class Meta:
        model = Candidate
        fields = ['shirt_size']
