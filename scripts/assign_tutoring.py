#!/usr/bin/env python
import sys

sys.path.insert(0, '..')

from tbpsite import settings
from django.core.management import setup_environ

setup_environ(settings)

from tutoring.models import Tutoring
from constants import TUTORING_DAY_CHOICES, TUTORING_HOUR_CHOICES

MAX_TUTORS_PER_HOUR = 5
MIN_TUTORS_PER_HOUR = 2  # Want this
ENFORCED_MIN_TUTORS_PER_HOUR = 1  # Enforce this

TUTORING_START = 10  # 10AM
TUTORING_END = 16  # 1 hr before 5pm

tutoringHours = {}
for d in TUTORING_DAY_CHOICES:
    for h in TUTORING_HOUR_CHOICES:
        tutoringHours[( int(d[0]), int(h[0]) + TUTORING_START )] = []

# Add all 'frozen' tutors to schedule
tutoringObjs = []
allTutors = []
for t in Tutoring.current.all():
    allTutors.append(t)
    allTutors.append(t)
    if t.frozen:
        tutoringHours[( int(t.day_1), int(t.hour_1) + TUTORING_START )].append(t)
        tutoringHours[( int(t.day_2), int(t.hour_2) + TUTORING_START )].append(t)
    else:
        tutoringObjs.append(t)


def tutoring_hours_status(enforce=False):
    min_satisfied = True
    max_satisfied = True
    total_assigned_hours = 0
    for slot in sorted(tutoringHours):
        assignees = tutoringHours[slot]
        for c in TUTORING_DAY_CHOICES:
            if int(c[0]) == slot[0]:
                print c[1], 'at',
                break
        time = slot[1] % 12
        if not time:
            time = 12
        print time, 'AM' if slot[1] < 12 else 'PM', ': ',
        print ', '.join(map(repr, assignees))

        total_assigned_hours += len(assignees)

        if len(assignees) < ENFORCED_MIN_TUTORS_PER_HOUR:
            print "*** The time slot above does not satisfy the minimum %d tutors per hour" % ENFORCED_MIN_TUTORS_PER_HOUR
            min_satisfied = False

        if len(assignees) > MAX_TUTORS_PER_HOUR:
            max_satisfied = False
            #if len( assignees ) < ENFORCED_MIN_TUTORS_PER_HOUR:
            #    print "*** The time slot above does not satisfy the minimum %d tutors per hour" % ENFORCED_MIN_TUTORS_PER_HOUR
            #    minSatisfied = False

    print 'There are', len(Tutoring.current.all()), 'tutoring objects'
    print 'Total %d tutoring hours per week' % total_assigned_hours

    if enforce:
        all_assigned = total_assigned_hours / len(Tutoring.current.all()) == 2

        print 'Minimum satisfied:', min_satisfied
        print 'Maximum satisfied:', max_satisfied
        print 'Everyone assigned:', all_assigned

        if not all_assigned:
            tutors = []
            for tutor in Tutoring.current.all():
                tutors.append(tutor)
                tutors.append(tutor)

            assert len(allTutors) == len(Tutoring.current.all()) * 2

            for time, assignees in tutoringHours.iteritems():
                for assignee in assignees:
                    tutors.remove(assignee)

            print tutors

        assert min_satisfied and max_satisfied and all_assigned


def assign_if_necessary():
    global tutoringObjs
    global tutoringHours

    # Assign if necessary
    for assignCount in range(ENFORCED_MIN_TUTORS_PER_HOUR, MIN_TUTORS_PER_HOUR + 1):
        hours_assigned = True
        while hours_assigned:
            hours_assigned = False

            # Each day
            for day in range(5):
                # Each even 2-hour slot
                for slot in range(TUTORING_START, TUTORING_END, 2):
                    tutor_count = 0
                    tutor_objs = []

                    for t in tutoringObjs:
                        for p in t.preferences(two_hour=False):
                            if p[0] == day and p[1] == slot:
                                tutor_count += 1
                                tutor_objs.append(t)
                                break

                    # Assign if we need to
                    if tutor_count and tutor_count + len(tutoringHours[(day, slot)]) <= assignCount:
                        hours_assigned = True
                        for t in tutor_objs:
                            tutoringObjs.remove(t)
                            tutoringHours[(day, slot)].append(t)
                            tutoringHours[(day, slot + 1)].append(t)


assign_if_necessary()

# Try filling min iterating through first, second, third prefs if BOTH hours unsatisfied
for pref in range(3):
    tutoringObjsCopy = tutoringObjs[:]
    for t in tutoringObjsCopy:
        day, slot = t.preferences(two_hour=False)[pref]
        if len(tutoringHours[(day, slot)]) < MIN_TUTORS_PER_HOUR \
                and len(tutoringHours[(day, slot + 1)]) < MIN_TUTORS_PER_HOUR:
            tutoringObjs.remove(t)

            tutoringHours[(day, slot)].append(t)
            tutoringHours[(day, slot + 1)].append(t)

assign_if_necessary()

# Try filling min iterating through first, second, third prefs if ANY hours unsatisfied
for pref in range(3):
    tutoringObjsCopy = tutoringObjs[:]
    for t in tutoringObjsCopy:
        day, slot = t.preferences(two_hour=False)[pref]
        if len(tutoringHours[(day, slot)]) < MIN_TUTORS_PER_HOUR \
                or len(tutoringHours[(day, slot + 1)]) < MIN_TUTORS_PER_HOUR:
            tutoringObjs.remove(t)

            tutoringHours[(day, slot)].append(t)
            tutoringHours[(day, slot + 1)].append(t)

assign_if_necessary()

# Try assigning everyone else iterating through first, second, third prefs
for pref in range(3):
    tutoringObjsCopy = tutoringObjs[:]
    for t in tutoringObjsCopy:
        day, slot = t.preferences(two_hour=False)[pref]
        if len(tutoringHours[(day, slot)]) < MAX_TUTORS_PER_HOUR \
                and len(tutoringHours[(day, slot + 1)]) < MAX_TUTORS_PER_HOUR:
            tutoringObjs.remove(t)

            tutoringHours[(day, slot)].append(t)
            tutoringHours[(day, slot + 1)].append(t)

# Last try, see if we can pull someone from another slot to fill MIN_TUTORS_PER_HOUR per slot
for timeSlot, assignees in tutoringHours.iteritems():
    # Slot unsatisfied
    if len(assignees) < MIN_TUTORS_PER_HOUR:
        for iterTimeSlot, iterAssignees in tutoringHours.iteritems():
            day, hour = iterTimeSlot
            # More tutors here than necessary
            if len(assignees) > MIN_TUTORS_PER_HOUR:
                # Find someone we can move
                for assignee in iterAssignees:
                    if assignee.frozen:
                        continue

                    # Is this slot in tutor's preferences?
                    reassignable = False
                    for pref in assignee.preferences(two_hour=True):
                        if timeSlot == (pref[0], pref[1][0]) \
                                or timeSlot == (pref[0], pref[1][1]):
                            reassignable = True
                            break

                    if not reassignable:
                        continue

                    # Second hour for this tutor is the hour before
                    if hour > TUTORING_START and assignee in tutoringHours[(day, hour - 1)]:
                        secondSlot = tutoringHours[(day, hour - 1)]
                    else:
                        secondSlot = tutoringHours[(day, hour + 1)]

                    # Second hour is also happy
                    if len(secondSlot) > MIN_TUTORS_PER_HOUR:
                        secondSlot.remove(t)
                        iterAssignees.remove(t)

                        tutoringHours[(pref[0], pref[1][0])].append(t)
                        tutoringHours[(pref[0], pref[1][1])].append(t)

# Enforce min and max per hour
tutoring_hours_status(enforce=False)

print tutoringObjs

# Validate assigned hours with preferences
for time, assignees in tutoringHours.items():
    for assignee in assignees:
        if assignee.frozen:
            assert (time[0] == int(assignee.day_1)
                    and time[1] == int(assignee.hour_1) + TUTORING_START) or \
                   (time[0] == int(assignee.day_2)
                    and time[1] == int(assignee.hour_2) + TUTORING_START)
        else:
            assert (time in assignee.preferences(two_hour=False) or
                    time in [(t[0], t[1] + 1) for t in assignee.preferences(two_hour=False)])

# Commit
for time, assignees in tutoringHours.items():
    for assignee in assignees:
        if allTutors.count(assignee) == 2:
            allTutors.remove(assignee)
            assignee.day_1 = str(time[0])
            assignee.hour_1 = str(time[1] - TUTORING_START)
        else:
            assignee.day_2 = str(time[0])
            assignee.hour_2 = str(time[1] - TUTORING_START)

        assignee.save()
