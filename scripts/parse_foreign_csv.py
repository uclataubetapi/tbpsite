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
from tutoring.models import DAY_CHOICES, HOUR_CHOICES, TWO_HOUR_CHOICES
from tutoring.models import Class
            
def parseDayChoices(choice):
    c = choice.split(':')[0]
    for i in range(len(DAY_CHOICES)):
        if DAY_CHOICES[i][1] == c:
            return str(i)

def parseTwoHourChoices(choice):
    c = choice.split(':')[1].replace(' ','')
    for i in range(len(TWO_HOUR_CHOICES)):
        if TWO_HOUR_CHOICES[i][1] == c:
            return [str(i),str(i+1)]#parseHourChoices(c)

def parseHourChoices(choices):
    c = choices.split('-')
    res = ['','']
    for i in range(len(HOUR_CHOICES)):
        if HOUR_CHOICES[i][1] == c[0]:
            res[0] = str(i)
        elif HOUR_CHOICES[i][1] == c[1]:
            res[1] = str(i-1)
    return res


fts = ForeignTutoring.objects.filter(term=Settings.objects.term())
tutors = Tutoring.objects.filter(term=Settings.objects.term())
users = User.objects.all()
fts.delete()
allClasses = Class.objects.all()

tbpTutors = False
csvFileName = sys.argv[1];
alreadyTutors = []
with open(csvFileName, 'rb') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        firstName = row["First Name"]
        if firstName == "TBP Room Tutoring":
            tbpTutors = True
        elif firstName == "HKN Room Tutoring":
            tbpTutors = False
        elif firstName != "" and tbpTutors:
            try:
                userProfile = users.get(first_name=firstName,last_name=row["Last Name"]).profile
                doesUserExist = tutors.get(profile=userProfile)
                alreadyTutors.append("User already tutoring for TBP : " + firstName + " " + row["Last Name"])
            except:
                print "Adding: " + firstName + " " + row["Last Name"]
                day = parseDayChoices(row["Tutoring Time"])
                hours = parseTwoHourChoices(row["Tutoring Time"])
                tutClasses = row["Tutorable Classes"].split(',')
                
                tutor = fts.create(name=row["First Name"]+" "+row["Last Name"],
                                   day_1=day,
                                   day_2=day,
                                   hour_1=hours[0],
                                   hour_2=hours[1],
                                   organization=0) #0 is for UPE
                for cl in tutClasses:
                    cParts = cl.split(' ')
                    if(cParts.count('')>0):
                        cParts.remove('')
                    try:
                        c = allClasses.get(department=cParts[0],course_number=cParts[1])
                        tutor.classes.add(c)
                    except Exception:
                        print "Failed to add this class : " + str(cParts)

for t in alreadyTutors:
    print t
print "Updating Schedule Page..."
os.system("sudo ~/tbpsite/manage.py updateschedule")
