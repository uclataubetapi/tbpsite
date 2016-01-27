#!/usr/bin/env python
from django.core.management import setup_environ
from tbpsite import settings
setup_environ(settings)

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from main.models import *
from main.admin import create_candidate
import csv, sys

if len(sys.argv) != 4:
    print('csv quarter year')
    exit()

term = Term.objects.get_or_create(quarter=sys.argv[2], year=sys.argv[3])[0]
print str(term.__unicode__()), 'y/n?',
if raw_input() != 'y':
    exit()

with open(sys.argv[1]) as f:
    for row in f:
        email = row[:-1] if row[-1] == '\n' else row
        try:
            user = User.objects.create_user(username=email, email=email)
        except IntegrityError:
            print email
            continue
        user.save()
        profile = Profile.objects.create(user=user, position='1', initiation_term=term)
                
