from django import forms
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm

CANDIDATE_COMMUNITY_SERVICE = 1
CANDIDATE_SOCIAL = 2
ACTIVE_MEMBER_SOCIAL = 2

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
        ('6', 'Materials Science and Engineering') )
PLACE_CHOICES = (
        ('0', 'Not Completed'),
        ('1', 'Completed'),
        ('2', '3rd'),
        ('3', '2nd'),
        ('4', '1st'),
        )
PLACE_POINTS = {
        '0': 0,
        '1': 0,
        '2': 5,
        '3': 10,
        '4': 25,
        }
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
GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        )
QUARTER_CHOICES = (
        ('0', 'Winter'),
        ('1', 'Spring'),
        ('2', 'Summer'),
        ('3', 'Fall'),
        )

fs = FileSystemStorage(location='/media')

def professor_interview_path(instance, filename=''):
    return 'professor_interviews/%s.pdf' % str(instance).replace(' ', '_')

class Term(models.Model):
    quarter = models.CharField(max_length=1, choices=QUARTER_CHOICES)
    year = models.IntegerField()

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
    
    resume = models.CharField(max_length=1, choices=PLACE_CHOICES, default='0')
    professor_interview = models.CharField(max_length=1, choices=PLACE_CHOICES, default='0')
    signature_book = models.CharField(max_length=1, choices=PLACE_CHOICES, default='0')
    candidate_quiz = models.CharField(max_length=1, choices=PLACE_CHOICES, default='0')
    other = models.IntegerField(default=0)

    objects = TermManager()

    class Meta:
        ordering = ('-term', 'house')
        unique_together = ('house', 'term')
        verbose_name_plural = "House Points"
                     
    def __unicode__(self):
        return self.house.__unicode__()

    def resume_points(self):
        return PLACE_POINTS[self.resume]

    def professor_interview_points(self):
        return PLACE_POINTS[self.professor_interview]

    def signature_book_points(self):
        return PLACE_POINTS[self.signature_book]

    def candidate_quiz_points(self):
        return PLACE_POINTS[self.candidate_quiz]

    def candidate_list(self):
        return Candidate.objects.select_related().filter(profile__house=self.house, term=self.term)

    def social(self):
        return sum(candidate.social_points() for candidate in self.candidate_list())

    def tutoring(self):
        return sum(candidate.tutoring_points() for candidate in self.candidate_list())

    def community_service(self):
        return sum(candidate.community_service_points() for candidate in self.candidate_list())

    def other_points(self):
        return sum(candidate.other for candidate in self.candidate_list()) + self.other

    def points(self):
        return sum([self.resume_points(), self.professor_interview_points(), self.signature_book_points(), self.candidate_quiz_points(),
            self.social(), self.tutoring(), self.community_service(), self.other_points()])

class Profile(models.Model):
    user = models.OneToOneField(User)
    middle_name = models.CharField(max_length=30, blank=True, verbose_name="Middle Name")
    nickname = models.CharField(max_length=30, blank=True, verbose_name="Nickname (optional)")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    birthday = models.DateField(null=True)
    phone_number = models.CharField(max_length=25, verbose_name="Phone Number")

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
    resume_pdf = models.DateTimeField(blank=True, null=True)
    resume_word = models.DateTimeField(blank=True, null=True)

    classes = models.ManyToManyField('tutoring.Class', blank=True, null=True)

    class Meta:
        ordering = ('position', 'user__last_name', 'user__first_name')

    def __unicode__(self):
        if self.nickname:
            return '{} {}'.format(self.nickname, self.user.last_name)
        name = self.user.get_full_name()
        return name if name else self.user.get_username()

    def resume(self):
        return self.resume_pdf or self.resume_word

    def dump(self):
        return ','.join(thing for thing in [self.user.first_name, self.middle_name, self.user.last_name, self.user.email, self.nickname, self.gender, 
            self.birthday.strftime('%x') if self.birthday else '', self.phone_number, self.get_major_display(), 
            self.initiation_term.__unicode__() if self.initiation_term else '', self.graduation_term.__unicode__() if self.graduation_term else ''])

class Candidate(models.Model):
    profile = models.OneToOneField('Profile')
    term = models.ForeignKey('Term')
    completed = models.BooleanField(default=False)

    tutoring = models.OneToOneField('tutoring.Tutoring', blank=True, null=True)
    bent_polish = models.BooleanField(default=False)
    candidate_quiz = models.BooleanField(default=False)
    candidate_meet_and_greet = models.BooleanField(default=False)
    signature_book = models.BooleanField(default=False)
    community_service = models.IntegerField(default=0)
    initiation_fee = models.BooleanField(default=False)
    engineering_futures = models.BooleanField(default=False)
    professor_interview = models.FileField(upload_to=professor_interview_path, storage=fs, 
            blank=True, null=True, default=None, verbose_name='Professor Interview (pdf)')
    other = models.IntegerField(default=0)

    current = TermManager()
    objects = models.Manager()

    class Meta:
        ordering = ('profile__user__last_name', 'profile__user__first_name')

    def __unicode__(self):
        return self.profile.__unicode__()

    def candidate_quiz_complete(self):
        return self.candidate_quiz != '0'

    def signature_book_complete(self):
        return self.signature_book != '0'

    def tutoring_complete(self):
        return self.tutoring.complete() if self.tutoring else False

    def tutoring_points(self):
        return self.tutoring.points() if self.tutoring else False

    def social_count(self):
        from event.models import Event
        return Event.objects.filter(attendees=self, term=self.term).count()

    def social_complete(self):
        return (self.social_count() >= CANDIDATE_SOCIAL)

    def social_points(self):
        return (0 if not social_complete() else 5 * (self.social_count() - CANDIDATE_SOCIAL))

    def community_service_complete(self):
        return self.community_service >= CANDIDATE_COMMUNITY_SERVICE

    def community_service_points(self):
        return (0 if not self.community_service_points() else 5 * (self.community_service - CANDIDATE_COMMUNITY_SERVICE))

    def points(self):
        return sum([PLACE_POINTS[self.signature_book], PLACE_POINTS[self.candidate_quiz], 
            self.social_points(), self.tutoring_points(), self.community_service_points(), self.other])

    def resume(self):
        return self.profile.resume()

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
                ('Professor Interview', self.professor_interview)
                )

    def complete(self):
        return all(requirement for name, requirement in self.requirements())

class ActiveMember(models.Model):
    profile = models.ForeignKey('Profile')
    term = models.ForeignKey('Term')
    completed = models.BooleanField(default=False)

    EMCC = '0'
    TUTORING = '1'
    COMMITTEE = '2'
    REQUIREMENT_CHOICES = (
            (EMCC, 'EMCC'),
            (TUTORING, 'Tutoring'),
            (COMMITTEE, 'Committee'),
            )
    requirement_choice = models.CharField(max_length=1, choices=REQUIREMENT_CHOICES, default='0')
    requirement_complete = models.BooleanField(default=False)
    tutoring = models.OneToOneField('tutoring.Tutoring', blank=True, null=True)

    current = TermManager()
    objects = models.Manager()

    def __unicode__(self):
        return self.profile.__unicode__()

    class Meta:
        unique_together = ('profile', 'term')
        ordering = ('term',)

    def requirement(self):
        if self.requirement_choice in (ActiveMember.EMCC, ActiveMember.COMMITTEE):
            return self.requirement_complete
        return self.tutoring.complete() if self.tutoring else False

    def social_complete(self):
        from event.models import Event
        return Event.objects.filter(attendees=self, term=self.term).count() >= ACTIVE_MEMBER_SOCIAL

    def requirements(self):
        return (
                (self.get_requirement_choice_display(), self.requirement()),
                ('Social', self.social_complete()),
                )

    def complete(self):
        return all(requirement for name, requirement in self.requirements())

class Officer(models.Model):
    position = models.CharField(max_length=30)
    rank = models.IntegerField()
    mail_alias = models.CharField(max_length=30)
    profile = models.ManyToManyField('Profile')

    def list_profiles( self ):
        return ', '.join( [ str( a ) for a in self.profile.all() ] )

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

class UserForm(ModelForm):

    def check_password(self, password):
        raise NotImplementedError

    def clean(self):
        cleaned_data = super(UserForm, self).clean()

        current_password, username, new_password, confirm_password = map(cleaned_data.get, 
                ('current_password', 'username', 'new_password', 'confirm_password'))

        if (any([username != self.instance.get_username(), new_password, confirm_password]) 
                and not current_password):
            self._errors['current_password'] = self.error_class(["Current password required."])

        if current_password and not self.check_password(current_password):
            self._errors['current_password'] = self.error_class(["Incorrect password."])

        if username != self.instance.get_username() and User.objects.filter(username=username).count():
            self._errors['username'] = self.error_class(["Username has already been taken."])

        if new_password != confirm_password:
            self._errors['confirm_password'] = self.error_class(["Passwords do not match."])

        return cleaned_data

class UserAccountForm(UserForm):
    current_password = forms.CharField(widget=forms.widgets.PasswordInput, 
            help_text="Required if changing username or password.", required=False, label="Current Password")
    username = forms.CharField(required=False)
    new_password = forms.CharField(widget=forms.widgets.PasswordInput, required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.widgets.PasswordInput, required=False, label="Confirm Password")

    class Meta:
        model = User
        fields = ['current_password', 'username', 'new_password', 'confirm_password']

    def check_password(self, password):
        return self.instance.check_password(password)

class RegisterForm(UserForm):
    current_password = forms.CharField(widget=forms.widgets.PasswordInput, 
            help_text="Required if changing username or password.", label="Registration Code")
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
    first_name = forms.CharField(required=True, label="First Name")
    last_name = forms.CharField(required=True, label="Last Name")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

class ProfileForm(ModelForm):
    graduation_quarter = forms.ChoiceField(choices=QUARTER_CHOICES, label="Graduation Quarter")
    graduation_year = forms.IntegerField(label="Graduation Year")

    class Meta:
        model = Profile
        fields = ['middle_name', 'nickname', 'gender', 'birthday', 'phone_number', 'major', 'graduation_quarter', 'graduation_year']
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
        fields = ['professor_interview']

class MemberForm(ModelForm):

    class Meta:
        model = ActiveMember
        fields = ['requirement_choice']
