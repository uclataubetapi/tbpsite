#!/usr/bin/env python
import sys

sys.path.insert(0, '..')

from tbpsite import settings
from django.core.management import setup_environ

setup_environ(settings)

from main.models import *
from tutoring.models import Tutoring

first_name = sys.argv[1] #raw_input("User's first name: ")
last_name = sys.argv[2] #raw_input("User's last name: ")

print first_name + " " + last_name

user = User.objects.get(first_name=first_name, last_name=last_name)
foo = Tutoring.with_weeks(user.profile, term=Settings.objects.term()) #with_weeks uses create, so we don't need to worry about saving

print "Tutoring object: " + foo + " created for " + first_name + " " + last_name
