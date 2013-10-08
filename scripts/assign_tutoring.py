#!/usr/bin/env python
import sys
sys.path.insert( 0, '..' )

from tbpsite import settings
from django.core.management import setup_environ

setup_environ( settings )

from tutoring.models import Tutoring, DAY_CHOICES, HOUR_CHOICES

MAX_TUTORS_PER_HOUR = 7 
MIN_TUTORS_PER_HOUR = 3 # Want this
ENFORCED_MIN_TUTORS_PER_HOUR = 2 # Enforce this

TUTORING_START = 10 # 10AM
TUTORING_END = 18 # 6 PM

tutoringHours = {}
for d in DAY_CHOICES:
    for h in HOUR_CHOICES:
        tutoringHours[ ( int( d[ 0 ] ), int( h[ 0 ] ) + TUTORING_START ) ] = []

def tutoringHoursStatus( enforce=False ):
    minSatisfied = True
    maxSatisfied = True
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

        if len( assignees ) < ENFORCED_MIN_TUTORS_PER_HOUR:
            print "*** The time slot above does not satisfy the minimum %d tutors per hour" % ENFORCED_MIN_TUTORS_PER_HOUR
            minSatisfied = False

        if len( assignees ) > MAX_TUTORS_PER_HOUR:
            maxSatisfied = False
        #if len( assignees ) < ENFORCED_MIN_TUTORS_PER_HOUR:
        #    print "*** The time slot above does not satisfy the minimum %d tutors per hour" % ENFORCED_MIN_TUTORS_PER_HOUR
        #    minSatisfied = False

    print 'There are', len( Tutoring.current.all() ), 'tutoring objects'
    print 'Total %d tutoring hours per week' % totalAssignedHours


    if enforce:
        allAssigned = totalAssignedHours / len( Tutoring.current.all() ) == 2        

        print 'Minimum satisfied:', minSatisfied
        print 'Maximum satsified:', maxSatisfied
        print 'Everyone assigned:', allAssigned
        assert minSatisfied and maxSatisfied and allAssigned

tutoringObjs = [ t for t in Tutoring.current.all() ]

def assignIfNecessary():
    global tutoringObjs
    global tutoringHours

    # Assign if necessary
    assignCount = MIN_TUTORS_PER_HOUR
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
                if tutorCount and tutorCount + len( tutoringHours[ ( day, slot ) ] ) <= assignCount:
                    hoursAssigned = True
                    for t in tutorObjs:
                        tutoringObjs.remove( t )
                        tutoringHours[ ( day, slot ) ].append( t )
                        tutoringHours[ ( day, slot + 1 ) ].append( t )

assignIfNecessary()

# Try filling min iterating through first, second, third prefs if BOTH hours unsatisfied
for pref in range( 3 ):
    tutoringObjsCopy = tutoringObjs[ : ]
    for t in tutoringObjsCopy:
        day, slot = t.preferences( twoHour=False )[ pref ]
        if len( tutoringHours[ ( day, slot ) ] ) < MIN_TUTORS_PER_HOUR \
            and len( tutoringHours[ ( day, slot + 1 ) ] ) < MIN_TUTORS_PER_HOUR:
            tutoringObjs.remove( t )

            tutoringHours[ ( day, slot ) ].append( t )
            tutoringHours[ ( day, slot + 1 ) ].append( t )

assignIfNecessary()

# Try filling min iterating through first, second, third prefs if ANY hours unsatisfied
for pref in range( 3 ):
    tutoringObjsCopy = tutoringObjs[ : ]
    for t in tutoringObjsCopy:
        day, slot = t.preferences( twoHour=False )[ pref ]
        if len( tutoringHours[ ( day, slot ) ] ) < MIN_TUTORS_PER_HOUR \
            or len( tutoringHours[ ( day, slot + 1 ) ] ) < MIN_TUTORS_PER_HOUR:
            tutoringObjs.remove( t )

            tutoringHours[ ( day, slot ) ].append( t )
            tutoringHours[ ( day, slot + 1 ) ].append( t )

assignIfNecessary()

# Try assigning everyone else iterating through first, second, third prefs
for pref in range( 3 ):
    tutoringObjsCopy = tutoringObjs[ : ]
    for t in tutoringObjsCopy:
        day, slot = t.preferences( twoHour=False )[ pref ]
        if len( tutoringHours[ ( day, slot ) ] ) < MAX_TUTORS_PER_HOUR \
            and len( tutoringHours[ ( day, slot + 1 ) ] ) < MAX_TUTORS_PER_HOUR:
            tutoringObjs.remove( t )

            tutoringHours[ ( day, slot ) ].append( t )
            tutoringHours[ ( day, slot + 1 ) ].append( t )

# Last try, see if we can pull someone from another slot to fill MIN_TUTORS_PER_HOUR per slot
for timeSlot, assignees in tutoringHours.iteritems():
    # Slot unsatisfied
    if len( assignees ) < MIN_TUTORS_PER_HOUR:
        for iterTimeSlot, iterAssignees in tutoringHours.iteritems():
            day, hour = iterTimeSlot
            # More tutors here than necessary
            if len( assignees ) > MIN_TUTORS_PER_HOUR:
                # Find someone we can move
                for assignee in iterAssignees:
                    # Is this slot in tutor's preferences?
                    reassignable = False
                    for pref in assignee.preferences( twoHour=True ):
                        if timeSlot == ( pref[ 0 ], pref[ 1 ][ 0 ] ) \
                            or timeSlot == ( pref[ 0 ], pref[ 1 ][ 1 ] ):
                            reassignable = True
                            break

                    if not reassignable:
                        continue
                    
                    # Second hour for this tutor is the hour before
                    if hour > TUTORING_START and assignee in tutoringHours[ ( day, hour - 1 ) ]:
                        secondSlot = tutoringHours[ ( day, hour - 1 ) ]
                    else:
                        secondSlot = tutoringHours[ ( day, hour + 1 ) ]

                    # Second hour is also happy
                    if len( secondSlot ) > MIN_TUTORS_PER_HOUR:
                        secondSlot.remove( t )
                        iterAssignees.remove( t )

                        tutoringHours[ ( pref[ 0 ], pref[ 1 ][ 0 ] ) ].append( t )
                        tutoringHours[ ( pref[ 0 ], pref[ 1 ][ 1 ] ) ].append( t )

# Enforce min and max per hour
tutoringHoursStatus( enforce=True )

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
