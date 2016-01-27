#!/usr/bin/env python
import sys
import csv
import os
sys.path.insert( 0, '..' )

from tbpsite import settings
from django.core.management import setup_environ
setup_environ( settings )

from main.models import Settings
from main.models import User
from tutoring.models import Tutoring
from tutoring.models import ForeignTutoring
from constants import TUTORING_DAY_CHOICES, TUTORING_HOUR_CHOICES, TWO_HOUR_CHOICES
from tutoring.models import Class
from constants import *

fts = ForeignTutoring.objects.filter(term=Settings.objects.term())
tutors = Tutoring.objects.filter(term=Settings.objects.term())
csvFileName = sys.argv[1];

hr1Choices = set()
hr2Choices = set()
hr3Choices = set()
hr4Choices = set()
hr5Choices = set()
hr6Choices = set()
hr7Choices = set()

#IN PROGRESS

header = ['Hours', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] 

with open(csvFileName, 'wb') as csvFile:
    writer = csv.writer(csvFile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    for t in tutors:
        classes = t.get_classes()
    
    
