#!/usr/bin/env python
import sys
sys.path.insert( 0, '..' )

from tbpsite import settings
from django.core.management import setup_environ

setup_environ( settings )

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from main.models import Officer
from main.models import Profile


GROUPS = {
    'Event': {'Social Chairs', 'Community Service', 'Academic Outreach', 'Mentorship Chairs',
               'Member Coordinators', 'Vice President', 'Senior Advisors', 'Alumna Advisor', 'Secretary', 'Treasurer', 'Tutoring Chairs', 'Education Outreach', 'Corporate Relations', 'Publicity Chairs', 'Project Chairs', 'Historian', 'Alumna Advisor'}, 
    'Main': {'Education Outreach', 'Academic Outreach', 'Secretary', 'Senior Advisors', 'Alumna Advisor', 'Vice President', 'Community Service',
             'Member Coordinators'}, 
    'Tutoring': {'Tutoring Chairs', 'Vice President', 'Senior Advisors', 'Secretary'}
} 

SUPERPOS = {"Webmaster", "President"}
SUPERCOOLPEOPLE = {"Rachel Fang"}
superLog = []

users = User.objects.all()
positions = Officer.objects.all()

def assignPermissions():
    for u in User.objects.all():
        u.is_superuser = False
        u.is_staff = False
        u.user_permissions.clear()
        u.save()
    for key in GROUPS:
        Group.objects.get(name=key).user_set.clear()
    for pos in positions:
        curr = Officer.objects.get(position=pos)
    #   print curr.list_profiles()
        profiles = curr.profile.all()#curr.list_profiles().split(',');
        print pos
        for prof in profiles:
            #RAY WAS A DUMB
            # stripped = prof.strip()
        #     foo = stripped.split(" ")
        #     if(foo[1]==''):
        #         foo.remove('')
        #     firstname = foo[0]
        #     lastname = foo[1];
        # #        print firstname + ' ' + lastname
        #     users = User.objects.filter(last_name=lastname)
        #     user = None
        #     if(users.count()>1):
        #         user = User.objects.get(username=users.get(first_name=firstname))
        #     else:
        #         user = list(users)[0]
            user = users.get(profile=prof);
            for key in GROUPS:
                for position in GROUPS[key]:
                    if(pos.position==position):
                        print "       " + key + ' added to:    ' + user.get_full_name()
                        group = Group.objects.get(name=key)
                        group.user_set.add(user)
                        break
            user.is_staff = True
            user.is_superuser = False
            for p in SUPERPOS:
                if(pos.position==p):
                    user.is_superuser = True
                    superLog.append("Superuser status granted to: " + user.get_full_name() + " as - " + p)
            user.save()
    g1 = Group.objects.get(name="Event")
    g2 = Group.objects.get(name="Main")
    g3 = Group.objects.get(name="Tutoring")
    g1.save()
    g2.save()
    g3.save()

    for p in SUPERCOOLPEOPLE:
        foo = p.split(" ")
        fName = foo[0]
        lName = foo[1]
        user = User.objects.get(first_name=fName, last_name=lName)
        user.is_staff = True
        user.is_superuser = True
        superLog.append("Superuser status granted to: " + user.get_full_name() + " as - A Really Cool Person")
        user.save()
    for sup in superLog:
        print sup
        
assignPermissions()
