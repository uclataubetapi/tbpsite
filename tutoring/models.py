from django.db import models
from django.forms import ModelForm
from constants import TUTORING_DAY_CHOICES, TUTORING_HOUR_CHOICES, TWO_HOUR_CHOICES

from main.models import Settings, TermManager
from points import *

import datetime


class Class(models.Model):
    DEPT_CHOICES = (
        ('BE', 'BE'),
        ('CEE', 'CEE'),
        ('CHEM', 'CHEM'),
        ('CHEME', 'CHEME'),
        ('CS', 'CS'),
        ('ECON', 'ECON'),
        ('EE', 'EE'),
        ('ENGR', 'ENGR'),
        ('LS', 'LS'),
        ('MAE', 'MAE'),
        ('MATH', 'MATH'),
        ('MGMT', 'MGMT'),
        ('MSE', 'MSE'),
        ('PHYSICS', 'PHYSICS'),
        ('STATS', 'STATS'),
    )
    department = models.CharField(max_length=10, choices=DEPT_CHOICES)
    course_number = models.CharField(max_length=10)
    display = models.BooleanField(default=False)

    class Meta:
        ordering = ('department', 'course_number')
        verbose_name_plural = "Classes"

    def __unicode__(self):
        return '{} {}'.format(self.department, self.course_number)


class BaseTutoring(models.Model):
    term = models.ForeignKey('main.Term', default=Settings.objects.term)
    day_1 = models.CharField(max_length=1, choices=TUTORING_DAY_CHOICES, default='0')
    hour_1 = models.CharField(max_length=1, choices=TUTORING_HOUR_CHOICES, default='0')
    day_2 = models.CharField(max_length=1, choices=TUTORING_DAY_CHOICES, default='0')
    hour_2 = models.CharField(max_length=1, choices=TUTORING_HOUR_CHOICES, default='0')

    class Meta:
        abstract = True

    def get_classes(self):
        """
        implement in child class
        :raise NotImplementedError:
        """
        raise NotImplementedError

    def display_classes(self):
        """
        :return:    list of all classes for tutoring object
        """
        return ', '.join(c.__unicode__() for c in self.get_classes() if c.display)

    def get_class_ids(self):
        """
        :return:    list of class ids for each class
        """
        return ' '.join(c.department + c.course_number + '_1' for c in self.get_classes() if c.display)


class Tutoring(BaseTutoring):
    profile = models.ForeignKey('main.Profile')

    best_day = models.CharField(max_length=1, choices=TUTORING_DAY_CHOICES, default='0', verbose_name="Best Day")
    best_hour = models.CharField(max_length=1, choices=TWO_HOUR_CHOICES, default='0', verbose_name="Best Hour")
    second_best_day = models.CharField(max_length=1, choices=TUTORING_DAY_CHOICES, default='0',
                                       verbose_name="Second Best Day")
    second_best_hour = models.CharField(max_length=1, choices=TWO_HOUR_CHOICES, default='2',
                                        verbose_name="Second Best Hour")
    third_best_day = models.CharField(max_length=1, choices=TUTORING_DAY_CHOICES, default='0',
                                      verbose_name="Third Best Day")
    third_best_hour = models.CharField(max_length=1, choices=TWO_HOUR_CHOICES, default='4',
                                       verbose_name="Third Best Hour")

    week_3 = models.OneToOneField('Week3')
    week_4 = models.OneToOneField('Week4')
    week_5 = models.OneToOneField('Week5')
    week_6 = models.OneToOneField('Week6')
    week_7 = models.OneToOneField('Week7')
    week_8 = models.OneToOneField('Week8')
    week_9 = models.OneToOneField('Week9')

    current = TermManager()
    objects = models.Manager()
    
    #Whether the tutoring assignment algorithm should consider this object
    frozen = models.BooleanField(default=False)

    #Whether the tutoring object should be shown on the schedule
    hidden = models.BooleanField(default=False)

    is_tutoring = models.BooleanField(default=False)
    last_start = models.DateTimeField(auto_now=False, auto_now_add=False,
                                      default=lambda: datetime.datetime.now() - datetime.timedelta(days=1))

    class Meta:
        ordering = ('-term', 'profile')
        unique_together = ('profile', 'term')
        verbose_name_plural = "Tutoring"

    def __unicode__(self):
        return self.profile.user.get_full_name()

    def get_classes(self):
        """


        :return:
        """
        return self.profile.classes.all()

    def get_weeks(self):
        """


        :return:
        """
        return [self.week_3, self.week_4, self.week_5, self.week_6, self.week_7, self.week_8, self.week_9]

    def complete(self):
        """


        :return:
        """
        return all(week.complete() for week in self.get_weeks())

    def points(self):
        """


        :return:
        """
        return sum(week.points() for week in self.get_weeks())

    def preferences(self, two_hour=False):
        """

        :param two_hour:
        :return:
        """

        def logical_hours(hour_choice):
            """

            :param hour_choice:
            :return:
            """
            if two_hour:
                return int(hour_choice) + 10, int(hour_choice) + 11

            return int(hour_choice) + 10

        return ((int(self.best_day), logical_hours(self.best_hour)),
                (int(self.second_best_day), logical_hours(self.second_best_hour)),
                (int(self.third_best_day), logical_hours(self.third_best_hour)))

    @classmethod
    def with_weeks(cls, profile, term):
        """

        :param profile:
        :param term:
        :return:
        """
        tutoring_weeks = {'week_{}'.format(d): globals()['Week{}'.format(d)].objects.create() for d in range(3, 10)}
        return cls.objects.create(profile=profile, term=term, **tutoring_weeks)


class WeekManager(models.Manager):
    def get_query_set(self):
        """


        :return:
        """
        if not Settings.objects.display_all_terms():
            term = Settings.objects.term()
            if term:
                return super(WeekManager, self).get_query_set().filter(tutoring__term=term)
        return super(WeekManager, self).get_query_set()


class Week(models.Model):
    hours = models.IntegerField(default=0)
    tutees = models.IntegerField(default=0)
    classes = models.ManyToManyField('Class', blank=True, null=True)
    no_makeup = models.BooleanField(default=True)

    objects = WeekManager()

    class Meta:
        abstract = True
        ordering = ('tutoring__day_1', 'tutoring__hour_1',
                    'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')

    def __unicode__(self):
        return self.profile().__unicode__()

    def complete(self):
        """


        :return:
        """
        return self.hours >= MIN_TUTORING_HOURS

    def points(self):
        """


        :return:
        """
        count = self.hours
        points = 0
        if count > MIN_TUTORING_HOURS:
            points += EXTRA_TUTORING_POINTS * min(count - MIN_TUTORING_HOURS, MAX_TUTORING_HOURS - MIN_TUTORING_HOURS)
        if self.no_makeup:
            points += TUTORING_POINTS * min(count, MIN_TUTORING_HOURS)
        return points

    def day_1(self):
        return self.tutoring.get_day_1_display()

    def day_2(self):
        return self.tutoring.get_day_2_display()

    def hour_1(self):
        return self.tutoring.get_hour_1_display()

    def hour_2(self):
        return self.tutoring.get_hour_2_display()

    def profile(self):
        return self.tutoring.profile

    def term(self):
        return self.tutoring.term


class Week3(Week):
    class Meta(Week.Meta):
        verbose_name_plural = "Week 3"


class Week4(Week):
    class Meta(Week.Meta):
        verbose_name_plural = "Week 4"


class Week5(Week):
    class Meta(Week.Meta):
        verbose_name_plural = "Week 5"


class Week6(Week):
    class Meta(Week.Meta):
        verbose_name_plural = "Week 6"


class Week7(Week):
    class Meta(Week.Meta):
        verbose_name_plural = "Week 7"


class Week8(Week):
    class Meta(Week.Meta):
        verbose_name_plural = "Week 8"


class Week9(Week):
    class Meta(Week.Meta):
        verbose_name_plural = "Week 9"


class ForeignTutoring(BaseTutoring):
    ORG_CHOICES = (
        ('0', '(UPE)'),
        ('1', '(HKN)'),
        ('2', '')
    )
    name = models.CharField(max_length=80)
    classes = models.ManyToManyField(Class)
    organization = models.CharField(max_length=1, choices=ORG_CHOICES)

    hidden = models.BooleanField(default=False)

    current = TermManager()
    objects = models.Manager()

    class Meta:
        ordering = ('-term', 'name')
        unique_together = ('name', 'term')
        verbose_name_plural = "Foreign Tutoring"

    def __unicode__(self):
        return self.name

    def get_classes(self):
        return self.classes.all()


class TutoringPreferencesForm(ModelForm):
    class Meta:
        model = Tutoring
        fields = ['best_day', 'best_hour', 'second_best_day', 'second_best_hour', 'third_best_day', 'third_best_hour']
