#!/usr/bin/env python
import sys
sys.path.insert( 0, '..' )

from tbpsite import settings
from django.core.management import setup_environ

setup_environ( settings )

from tutoring.models import Tutoring, DAY_CHOICES, HOUR_CHOICES

MAX_TUTORS_PER_HOUR = 6
MIN_TUTORS_PER_HOUR = 2

TUTORING_START = 10 # 10AM
TUTORING_END = 18 # 6 PM

tutoringHours = {}
for d in DAY_CHOICES:
    for h in HOUR_CHOICES:
        tutoringHours[ ( int( d[ 0 ] ), int( h[ 0 ] ) + TUTORING_START ) ] = []

tutoringObjs = [ t for t in Tutoring.current.all() ]

assignCount = MIN_TUTORS_PER_HOUR
while assignCount <= MAX_TUTORS_PER_HOUR:
    hoursAssigned = True 
    while hoursAssigned:
        hoursAssigned = False

        # Each day
        for day in range( 5 ):
            # Each even 2-hour slot
            for slot in range( TUTORING_START, TUTORING_END, 2 ):
                tutorCount = 0
                tutorObjs = []

                for t in tutoringObjs:
                    for p in t.preferences( twoHour=False ):
                        if p[ 0 ] == day and p[ 1 ] == slot:
                            tutorCount += 1
                            tutorObjs.append( t )
                            break

                # Assign if we need to
                if tutorCount and tutorCount <= assignCount and len( tutoringHours[ ( day, slot ) ] ) < MIN_TUTORS_PER_HOUR:
                    hoursAssigned = True
                    for t in tutorObjs:
                        tutoringObjs.remove( t )
                        tutoringHours[ ( day, slot ) ].append( t )
                        tutoringHours[ ( day, slot + 1 ) ].append( t )

    assignCount += 1

# Try assigning everyone else based on preferences
for t in tutoringObjs:
    hoursAssigned = False
    for p in t.preferences( twoHour=True ):
        if any( [ len( tutoringHours[ p[ 0 ], hour ] ) >= MAX_TUTORS_PER_HOUR for hour in p[ 1 ] ] ):
            continue

        tutoringHours[ ( p[ 0 ], p[ 1 ][ 0 ] ) ].append( t )
        tutoringHours[ ( p[ 0 ], p[ 1 ][ 1 ] ) ].append( t )

        hoursAssigned = True
        break

    if not hoursAssigned:
        print "Tutoring hours were not assigned for", t.profile

# Fill unfilled slots
for time, assignees in tutoringHours.items():
    if len( assignees ) < MIN_TUTORS_PER_HOUR:
        for day in range( 5 ):
            for slot in range( TUTORING_START, TUTORING_END, 2 ):
                # Can we can pull someone from this slot?
                if len( tutoringHours[ ( day, slot ) ] ) > MIN_TUTORS_PER_HOUR:
                    for t in tutoringHours[ ( day, slot ) ]:
                        if time in t.preferences( twoHour=False ):
                            slotBefore = tutoringHours.get( ( day, slot - 1 ) )
                            slotAfter = tutoringHours.get( ( day, slot + 1 ) )

                            # Remove tutor from original slots
                            tutoringHours[ ( day, slot ) ].remove( t )
                            if slotBefore and t in slotBefore:
                                slotBefore.remove( t )
                            else:
                                assert t in slotAfter
                                slotAfter.remove( t )

                            # Reassign
                            tutoringHours[ time ].append( t )
                            tutoringHours[ ( time[ 0 ], time[ 1 ] + 1 ) ].append( t )

minSatisfied = True
totalAssignedHours = 0
for slot in sorted( tutoringHours ):
    assignees = tutoringHours[ slot ]
    for c in DAY_CHOICES:
        if int( c[ 0 ] ) == slot[ 0 ]:
            print c[ 1 ], 'at',
            break
    time = slot[ 1 ] % 12
    if not time:
        time = 12
    print time, 'AM' if slot[ 1 ] < 12 else 'PM', ': ',
    print ', '.join( [ repr( assignee ) for assignee in assignees ] )

    totalAssignedHours += len( assignees )

    if len( assignees ) < MIN_TUTORS_PER_HOUR:
        print "*** The time slot above does not satisfy the minimum %d tutors per hour" % MIN_TUTORS_PER_HOUR
        minSatisfied = False

print 'There are', len( Tutoring.current.all() ), 'tutoring objects'
print 'Total %d tutoring hours per week' % totalAssignedHours

assert minSatisfied and totalAssignedHours / len( Tutoring.current.all() ) == 2

# Validate assigned hours with preferences
for time, assignees in tutoringHours.items():
    for assignee in assignees:
        assert time in assignee.preferences( twoHour=False ) or \
               time in [ ( t[ 0 ], t[ 1 ] + 1 ) for t in assignee.preferences( twoHour=False ) ]

# Commit
for time, assignees in tutoringHours.items():
    if time[ 1 ] % 2:
        continue

    for assignee in assignees:
        assignee.day_1 = str( time[ 0 ] )
        assignee.hour_1 = str( time[ 1 ] - TUTORING_START )
        assignee.day_2 = str( time[ 0 ] )
        assignee.hour_2 = str( time[ 1 ] + 1 - TUTORING_START )

        assignee.save()
