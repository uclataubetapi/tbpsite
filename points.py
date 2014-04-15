TUTORING_POINTS = 2 #per week
MIN_TUTORING_HOURS = 2 #per week
EXTRA_TUTORING_POINTS = 2 #per hour
MAX_TUTORING_HOURS = 4 # not sure what this is used for, says Rachel

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
QUIZ_POINTS = {
    #tuple(range(80, 90)): 4,
    #tuple(range(90, 100)): 6,
    #tuple(range(100, 120)): 8,
}

HOUSE_SOCIAL_POINTS = {
    #tuple(range(50, 70)): 1,
    #tuple(range(70, 100)): 2,
    #tuple(range(100, 101)): 3,
}

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
    FIRST: 6,
    SECOND: 4,
    THIRD: 2,
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

def house_social_points(score):
    if score < 50:
        return 0
    elif score < 70:
        return 1
    elif score < 100:
        return 2
    
    return 3
