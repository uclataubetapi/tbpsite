import os
import re
import datetime

from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

from constants import MAJOR_CHOICES, DEPT_CHOICES, resume_word_fs, resume_pdf_fs, community_service_fs, \
    professor_interview_fs

from points import *


def validate_re(regex, value, msg):
    if not re.match(regex, value):
        raise ValidationError(msg)


def upload_to_path(instance, filename):
    """
    Rename files that are uploaded
    """
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

    def get_week(self):
        """
        :return: Current week of term
        """
        week = (datetime.date.today() - self.start_date).days / 7 + 1
        if week < 3:
            return 3
        elif week > 9:
            return 9
        return week


class SettingsManager(models.Manager):
    def settings(self):
        """
        :return: Singleton Settings object
        """
        return super(SettingsManager, self).get_or_create(id=1)[0]

    def term(self):
        return self.settings().term

    def signup_term(self):
        return self.settings().signup_term

    def display_all_terms(self):
        return self.settings().display_all_terms

    def display_tutoring(self):
        return self.settings().display_tutoring

    def get_registration_code(self):
        return self.settings().registration_code

    def get_eligibility_list(self):
        return self.settings().eligibility_list


class Settings(models.Model):
    term = models.ForeignKey('Term', blank=True, null=True, related_name='current')
    signup_term = models.ForeignKey('Term', blank=True, null=True, related_name='signup')
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
        """
        :return: Current term if display_all_terms is not set in Settings and term is set, otherwise all terms
        """
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

    def member_list(self):
        """
        :return: Candidates and members in the house for the term
        """
        return (list(Candidate.objects.select_related().filter(profile__house=self.house, term=self.term)) +
                list(ActiveMember.objects.select_related().filter(profile__house=self.house, term=self.term)))

    def professor_interview_and_resume_points(self):
        """
        :return: N points for each person depending on the house ranking
        """
        return DOCUMENT_POINTS[self.professor_interview_and_resume] * Candidate.objects.select_related().filter(
            profile__house=self.house, term=self.term).count()

    def points(self):
        """
        :return: Total number of points for the house, including members
        """
        return sum([sum(member.points() for member in self.member_list()),
                    self.professor_interview_and_resume_points(), self.other])


class Profile(models.Model):
    user = models.OneToOneField(User)

    middle_name = models.CharField(max_length=30, blank=True, verbose_name="Middle Name")
    nickname = models.CharField(max_length=30, blank=True, verbose_name="Preferred Name (optional)")
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    birthday = models.DateField(null=True, verbose_name="Birthday (mm/dd/yyyy)")
    phone_number = models.CharField(max_length=25, verbose_name="Phone Number (xxx-xxx-xxxx)",
                                    validators=[lambda v: validate_re(r'^\d{3}-\d{3}-\d{4}$', v,
                                                                      'Please enter a valid phone number')])
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
        name = self.user.get_full_name()
        if self.nickname:
            name += ' (%s)' % (self.nickname)
        return name if name else self.user.get_username()

    def current(self):
        """
        :return: Requirement object associated with current term
        """
        if self.position == Profile.CANDIDATE:
            try:
                self.candidate.peer_teaching.tutoring
            except Candidate.DoesNotExist:
                return False
        elif self.position == Profile.MEMBER:
            try:
                ActiveMember.objects.get(profile=self, term=Settings.objects.term())
            except ActiveMember.DoesNotExist:
                return False
        return True

    def dump(self):
        """
        :return: Comma delimited fields of profile
        """
        return ','.join(field for field in [self.user.first_name, self.middle_name, self.user.last_name,
                                            self.user.email, self.nickname,
                                            self.house.__unicode__() if self.house else '', self.gender,
                                            self.birthday.strftime('%x') if self.birthday else '', self.phone_number,
                                            self.get_major_display(),
                                            self.initiation_term.__unicode__() if self.initiation_term else '',
                                            self.graduation_term.__unicode__() if self.graduation_term else ''])


class PeerTeaching(models.Model):
    #complete = models.BooleanField(default=False)
    ACAD_OUTREACH = '0'
    TUTORING = '1'
    REQUIREMENT_CHOICES = (
        (TUTORING, 'Tutoring'),
        (ACAD_OUTREACH, 'Academic Outreach Committee'),
    )
    requirement_choice = models.CharField(max_length=1, choices=REQUIREMENT_CHOICES, default='0')
    tutoring = models.OneToOneField('tutoring.Tutoring', blank=True, null=True)
    academic_outreach_complete = models.BooleanField(default=False)

    profile = models.ForeignKey('Profile', blank=True, null=True)

    term = models.ForeignKey('Term', blank=True, null=True)
    current = TermManager()
    objects = models.Manager()

    def isComplete(self):
        if self.requirement_choice == self.ACAD_OUTREACH:
            return self.academic_outreach_complete
        elif self.requirement_choice == self.TUTORING:
            return self.tutoring.complete() if self.tutoring else False
        else:
            return False

    def get_req_choice(self):
        return {
            self.TUTORING: 'Tutoring',
            self.ACAD_OUTREACH: 'Academic Outreach Committee',
        }[self.requirement_choice]

    def __unicode__(self):
        try:
            return self.profile.user.get_full_name()
        except AttributeError:
            return "Unkown Profile"
        
class Member(models.Model):
    profile = None
    term = models.ForeignKey('Term')

    peer_teaching = models.OneToOneField(PeerTeaching, blank=True, null=True)

    #The tutoring field is no longer used. References to Tutoring via a Member object now go though
    #the peer_teaching object. However as of yet there seems to a bug with removing this field
    #as django seems to have behind the scenes created an extra 'fieldname'_id attribute for 
    #some fields in the model including the tutoring field. Some sort of reference to this tutoring_id
    #field in the model remains even when you remove the tutoring field itself and migrate, thus after the
    #migrate django begins to throw errors where it cannot locate a tutoring_id field in the database
    #This needs to be looked into but is not a fatal level issue as the existence of this legacy field is 
    #not apparent to the user
    tutoring = models.OneToOneField('tutoring.Tutoring', blank=True, null=True)
    completed = models.BooleanField(default=False)
    other = models.IntegerField(default=0)

    event_requirements = models.ManyToManyField('Requirement')

    current = TermManager()
    objects = models.Manager()

    def __unicode__(self):
        return self.profile.__unicode__()

    class Meta:
        abstract = True
        ordering = ('term', 'profile__user__last_name', 'profile__user__first_name')

    
    def get_reqpoints_in_cat(self, category):
        sum = 0
        for r in self.event_requirements.all().values():
            if r['requirement_choice'] == category:
                sum += r['point_value']
        return sum

    def social_count(self):
        from event.models import Event

        return (Event.current.filter(attendees=self.profile, term=self.term, event_type=Event.SOCIAL).count() +
                Event.current.filter(attendees=self.profile, term=self.term, event_type=Event.HOUSE).count())

    # REQUIREMENTS
    def peer_teaching_complete(self):
        #return self.tutoring.complete() if self.tutoring else False
        return self.peer_teaching.isComplete() if self.peer_teaching else False

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
    #requirement_complete = models.BooleanField(default=False)

    
    shirt_size = models.CharField(max_length=2, default='M', choices=SHIRT_SIZES, verbose_name="T-Shirt Size")
    bent_polish = models.BooleanField(default=False)
    candidate_quiz = models.IntegerField(default=0)
    candidate_meet_and_greet = models.BooleanField(default=False)
    signature_book = models.BooleanField(default=False)
    community_service_proof = models.FileField(upload_to=upload_to_path, storage=community_service_fs, blank=True,
                                               null=True, default=None, verbose_name="Community Service Proof")
    community_service = models.IntegerField(default=0)
    initiation_fee = models.BooleanField(default=False)

    #required events
    engineering_futures = models.BooleanField(default=False)
    candidate_sorting = models.BooleanField(default=False)

    professor_interview = models.FileField(upload_to=upload_to_path, storage=professor_interview_fs,
                                           blank=True, null=True, default=None, verbose_name="Professor Interview")
    tbp_event = models.BooleanField(default=False)

    def get_peer_req_choice(self):
        return self.peer_teaching.get_req_choice()

    def resume(self):
        return self.profile.resume_pdf or self.profile.resume_word

    # REQUIREMENTS
    def community_service_complete(self):
        return self.community_service >= MIN_COMMUNITY_SERVICE

    def tbp_event_complete(self):
        return self.professor_interview or self.tbp_event

    def requirements(self):
        return (
            ('Peer Teaching', self.peer_teaching_complete()),
            ('Bent Polish', self.bent_polish),
            ('Candidate Quiz', self.candidate_quiz),
            ('Candidate Meet and Greet', self.candidate_meet_and_greet),
            ('Signature Book', self.signature_book),
            ('Community Service', self.community_service_complete()),
            ('Initiation Fee', self.initiation_fee),
            ('Engineering Futures', self.engineering_futures),
            ('Social', self.social_complete()),
            ('Resume', self.resume()),
            ('TBP event', self.tbp_event_complete()),
            ('Candidate Sorting', self.candidate_sorting),
        )

    def requirement_count(self):
        return len([None for _, requirement in self.requirements() if requirement])

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

    #not used anymore, added TBP event!
    def professor_interview_on_time_points(self):
        return ON_TIME_POINTS if self.professor_interview_on_time else 0

    def tbp_event_points(self):
        if self.tbp_event:
            from event.models import Event

            count = Event.objects.filter(attendees=self.profile, term=self.term).count()
            return TBP_EVENT_POINTS + (count - 1) * EXTRA_TBP_EVENT_POINTS
        else:
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
            self.tbp_event_points(), self.resume_on_time_points(), self.bent_polish_points(),
            self.quiz_first_try_points(), quiz_points(self.candidate_quiz), self.other,
        ))


class ActiveMember(Member):
    profile = models.ForeignKey('Profile')

    EMCC = '0'
    TUTORING = '1'
    HOUSE_LEADER = '2'
    COMMITTEE = '3'  # RG
    POKER = '4'
    CBR = '5'
    ACAD_OUTREACH = '6'
    REQUIREMENT_CHOICES = (
        (EMCC, 'EMCC'),
        (TUTORING, 'Tutoring'),
        (HOUSE_LEADER, 'House Leader'),
        # (POKER, 'Poker Tournament Committee'),
        # TODO: comment as necessary
        (COMMITTEE, 'Rube Goldberg Committee'),
        # (CBR, 'Cardboard Boat Race Committee'),
        (ACAD_OUTREACH, 'Academic Outreach'),
    )
    requirement_choice = models.CharField(max_length=1, choices=REQUIREMENT_CHOICES, default='0')
    requirement_complete = models.BooleanField(default=False)

    class Meta(Member.Meta):
        unique_together = ('profile', 'term')

    def social_count(self):
        from event.models import Event

        return Event.objects.filter(attendees=self.profile, term=self.term).count()

    def requirement(self):
        #allow for override in requirement
        return self.requirement_complete or self.peer_teaching_complete()

    def requirements(self):
        return (
            (self.get_requirement_choice_display(), self.requirement()),
            ('Events', self.social_complete()),
        )

    def points(self):
        if self.profile.user.is_staff or self.requirement_choice == self.HOUSE_LEADER:
            return 0
        else:
            return super(ActiveMember, self).points()


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

class Requirement(models.Model):
    
    SOCIAL = '0'
    PROFESSIONAL = '1'
    SERVICE = '2'
    CATEGORY_CHOICES = (
        (SOCIAL, 'Social'),
        (PROFESSIONAL, 'Professional'),
        (SERVICE, 'Service') 
    )

    name = models.CharField(max_length=40)
    requirement_choice = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='0')
    point_value = models.IntegerField(default=0)
    term = models.ForeignKey('Term')
    
    current = TermManager()
    objects = models.Manager()

    def __unicode__(self):
        return self.name

    def req_plain_text():
        return {
            SOCIAL: '0',
            PROFESSIONAL:'1',
            SERVICE: '2',
        }[requirement_choice]
