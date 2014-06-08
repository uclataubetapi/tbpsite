"""
This module containts constants specific to the house point system.
"""

TUTORING_POINTS = 2 #per week
MIN_TUTORING_HOURS = 2 #per week
EXTRA_TUTORING_POINTS = 2 #per hour
MAX_TUTORING_HOURS = 4 

COMMUNITY_SERVICE_POINTS = 6 
MIN_COMMUNITY_SERVICE = 1
EXTRA_COMMUNITY_SERVICE_POINTS = 12

SOCIAL_POINTS = 3 #per event
MIN_SOCIALS = 2
EXTRA_SOCIAL_POINTS = 6 #per event

TBP_EVENT_POINTS = 6
MIN_TBP_EVENTS = 1
EXTRA_TBP_EVENT_POINTS = 12

ON_TIME_POINTS = 2
INTERVIEW_ON_TIME_POINTS = 4
BENT_POLISH_POINTS = 2

QUIZ_FIRST_TRY_POINTS = 2

REQUIRED_EVENT_POINTS = 2 #candidate sorting, meet and greet, EF

FIRST = '1'
SECOND = '2'
THIRD = '3'
FOURTH = '4'
PLACE_CHOICES = (
    (FIRST, '1st'),
    (SECOND, '2nd'),
    (THIRD, '3rd'),
    (FOURTH, '4th'),
)
DOCUMENT_POINTS = {
    FIRST: 3,
    SECOND: 2,
    THIRD: 1,
    FOURTH: 0,
}


def quiz_points(score):
    if score < 80:
        return 0
    elif score < 90:
        return 4
    elif score < 100:
        return 6
    
    return 8

