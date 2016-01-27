#!/usr/bin/env python
from django.core.management import setup_environ
from tbpsite import settings
setup_environ(settings)

from os import path
import os
import shutil
import time
from datetime import date, timedelta, datetime
from main.models import Profile

MAJOR_MAPPING = {
'0' : 'AeroE',
'1' : 'BE',
'2' : 'ChemE',
'3' : 'CivilE',
'4' : 'CS',
'5' : 'CSE',
'6' : 'EE',
'7' : 'MatE',
'8' : 'MechE'}

SRC_DIR = '/home/tbpofficer/tbpsite/resumes'
DST_DIR = '/home/tbpofficer/resumes'
if not path.exists(DST_DIR):
	os.makedirs(DST_DIR)

for profile in Profile.objects.all():
    if profile.resume is None or datetime.today().date() - profile.resume.date() > timedelta(365):
        continue

    src_path = path.join(SRC_DIR, str(profile.user.id))

    directory = path.join(path.abspath(DST_DIR), profile.get_major_display())
    if not path.exists(directory):
        os.makedirs(directory)

    dst_resume = "%s%s%s_%s%s.pdf" % (profile.resume.year, str(profile.resume.month).rjust(2, '0'),
            MAJOR_MAPPING[profile.major], profile.user.first_name[0], profile.user.last_name)
    dst_path = path.join(directory, dst_resume)
    shutil.copy(src_path, dst_path)
