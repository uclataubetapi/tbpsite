import os.path, sys, time, datetime

sys.path.insert( 0, '..' )

from tbpsite import settings
from django.core.management import setup_environ

setup_environ( settings )

from main.models import Candidate

due_date = datetime.datetime(2013, 11, 8, 23, 59, 59)

print "Due date is %s" % due_date

due_date_seconds = time.mktime(due_date.timetuple())

for c in Candidate.objects.all():
    if not c.professor_interview:
        print "Missing professor interview: %s" % c
    elif os.path.getmtime(c.professor_interview.file.name) > due_date_seconds:
        print "Late professor interview: %s (%s)" % (c, datetime.datetime.fromtimestamp(os.path.getmtime(c.professor_interview.file.name)))
    if not c.resume():
        print "Missing resume: %s" % c
    elif os.path.getmtime(c.resume().file.name) > due_date_seconds:
        print "Late resume: %s (%s)" % (c, datetime.datetime.fromtimestamp(os.path.getmtime(c.resume().file.name)))
