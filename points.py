TUTORING_POINTS = 2
MIN_TUTORING_HOURS = 2
EXTRA_TUTORING_POINTS = 5
MAX_TUTORING_HOURS = 4

COMMUNITY_SERVICE_POINTS = 6
MIN_COMMUNITY_SERVICE = 1
EXTRA_COMMUNITY_SERVICE_POINTS = 15

SOCIAL_POINTS = 2
MIN_SOCIALS = 2
EXTRA_SOCIAL_POINTS = 5

ON_TIME_POINTS = 6
BENT_POLISH_POINTS = 2

QUIZ_FIRST_TRY_POINTS = 2
QUIZ_POINTS = {
    tuple(range(80, 90)): 5,
    tuple(range(90, 100)): 10,
    tuple(range(100, 101)): 15,
}

HOUSE_SOCIAL_POINTS = {
    tuple(range(50, 70)): 1,
    tuple(range(70, 100)): 2,
    tuple(range(100, 101)): 3,
}

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
    for bracket, points in QUIZ_POINTS.iteritems():
        if score in bracket:
            return points
    return 0
