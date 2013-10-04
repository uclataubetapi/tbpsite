import re

from main.models import Settings
from tutoring.models import Tutoring, ForeignTutoring, Class, HOUR_CHOICES, DAY_CHOICES
from common import render

number = re.compile(r'\d+')
numbers = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen']


def schedule(request):
    term = Settings.objects.term()
    tutors = []
    for hour, hour_name in HOUR_CHOICES:
        tutors_for_hour = []
        for day, day_name in DAY_CHOICES:
            if Settings.objects.display_tutoring() or (request.user.is_authenticated and request.user.is_staff):
                tutors_for_hour.append(list(Tutoring.current.filter(hour_1=hour, day_1=day)) +
                                       list(Tutoring.current.filter(hour_2=hour, day_2=day)) +
                                       list(ForeignTutoring.current.filter(hour_1=hour, day_1=day)) +
                                       list(ForeignTutoring.current.filter(hour_2=hour, day_2=day)))
            else:
                tutors_for_hour.append(None)
        tutors.append((hour_name, tutors_for_hour))

    classes = []
    for department, number in zip(Class.DEPT_CHOICES, numbers):
        department, _ = department
        courses = [(cls.course_number, cls.department+cls.course_number)
                   for cls in sorted((c for c in Class.objects.filter(department=department, display=True) if c.profile_set.all()),
                                     key=lambda c: tuple(int(s) if s.isdigit() else s
                                                         for s in re.search(r'(\d+)([ABCD]?L?)?',
                                                                            c.course_number).groups()))]
        if courses:
            classes.append((department, courses, 'collapse{}'.format(number)))
            
    return render(request, 'schedule.html', {'term': term, 'classes': classes, 'tutors': tutors,
                                             'display': request.user.is_staff or Settings.objects.display_tutoring()})


def feedback(request):
    return render(request, 'tutoring_feedback.html')
