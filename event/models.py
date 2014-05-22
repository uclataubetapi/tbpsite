import datetime

from django.db import models

from main.models import TermManager, Settings, Candidate, Profile
from points import house_social_points


class Event(models.Model):
    SOCIAL = '0'
    HOUSE = '3'
    EVENT_TYPE_CHOICES = (
        (SOCIAL, 'Social'),
        ('1', 'Project'),
        ('2', 'Mentorship'),
        (HOUSE, 'House'),
        ('4', 'Infosession'),
        ('5', 'Academic Outreach'),
    )

    term = models.ForeignKey('main.Term', default=Settings.objects.term)
    name = models.CharField(max_length=40)
    url = models.CharField(max_length=20, unique=True)
    description = models.TextField(max_length=1000)
    start = models.DateTimeField()
    end = models.DateTimeField()
    display_time = models.BooleanField(default=True)
    location = models.CharField(max_length=80)
    event_type = models.CharField(max_length=1, choices=EVENT_TYPE_CHOICES)
    image = models.ImageField(upload_to='events', blank=True, null=True)
    dropdown = models.BooleanField()
    attendees = models.ManyToManyField('main.Profile', blank=True, null=True)

    current = TermManager()
    objects = models.Manager()

    class Meta:
        ordering = ('end', '-term', 'name')
        unique_together = ('name', 'term')

    def __unicode__(self):
        return self.name

    def is_same_day(self):
        return self.start.date() == self.end.date()

    def is_upcoming(self):
        return self.end < datetime.datetime.today()

    def get_start(self):
        if self.display_time:
            return self.start.strftime("%a, %m/%d/%y %I:%M%p")
        return self.start.strftime("%a, %m/%d/%y")

    def get_end(self):
        if self.display_time:
            return self.end.strftime("%a, %m/%d/%y %I:%M%p")
        return self.end.strftime("%a, %m/%d/%y")

    def get_date(self):
        return '{}{}'.format(self.start.strftime("%a, %m/%d/%y"), '' if self.is_same_day() else self.end.strftime("-%a, %m/%d/%y"))

    def get_time(self):
        if self.display_time:
            return "%s - %s" % (self.start.strftime("%I:%M %p"), self.end.strftime("%I:%M %p"))
        return ''

    def get_datetime(self):
        if self.is_same_day():
            return '{}{}'.format(self.get_start(), self.end.strftime("-%I:%M%p") if self.display_time else '')
        return '{}-{}'.format(self.get_start(), self.get_end())

    def points(self, house):
        total_members = set(Candidate.objects.filter(term=self.term, profile__house=house))
        total_attendees = set(profile.candidate for profile in
                              self.attendees.filter(house=house, position=Profile.CANDIDATE)) & total_members
        if not total_attendees:
            return 0
        percentage = len(total_members) * 100 / len(total_attendees)
        return house_social_points(percentage)

    def save(self, *args, **kwargs):
        if self.event_type == '2' or self.event_type == '5':
            for profile in self.attendees.filter(position=Profile.CANDIDATE):
                profile.candidate.tbp_event = True
                profile.candidate.save()
                profile.save()
        super(Event, self).save(*args, **kwargs)
