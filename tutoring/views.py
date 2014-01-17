import os
import itertools
import re

import datetime

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.template import TemplateDoesNotExist, Context, Template
from django.shortcuts import get_object_or_404

from common import render
from main.models import Settings, Profile
from tbpsite.settings import BASE_DIR
from tutoring.models import Tutoring, ForeignTutoring, Class, HOUR_CHOICES, DAY_CHOICES

number = re.compile(r'\d+')
numbers = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen']


def get_classes():
    classes = []
    for department, number in zip(Class.DEPT_CHOICES, numbers):
        department, _ = department
        courses = [(cls.course_number, cls.department+cls.course_number)
                   for cls in sorted((c for c in Class.objects.filter(department=department, display=True)
                                      if any(filter(Profile.current, c.profile_set.all()))),
                                     key=lambda c: tuple(int(s) if s.isdigit() else s
                                                         for s in re.search(r'(\d+)([ABCD]?L?)?',
                                                                            c.course_number).groups()))]
        if courses:
            classes.append((department, courses, 'collapse{}'.format(number)))
    return classes


def get_tutors():
    tutors = []
    for hour, hour_name in HOUR_CHOICES:
        tutors_for_hour = []
        tutoring_objs = [t for t in Tutoring.current.all()] + [t for t in ForeignTutoring.current.all()]
        for day, day_name in DAY_CHOICES:
            tutors_for_hour.append(
                sorted([t for t in tutoring_objs
                        if (t.hour_1 == hour and t.day_1 == day) or (t.hour_2 == hour and t.day_2 == day)],
                       key=lambda t: t.__unicode__()))
        tutors.append((hour_name, tutors_for_hour))
    return tutors


def schedule(request):
    term = Settings.objects.term()
    if Settings.objects.display_tutoring():
        try:
            return render(request, 'schedule.html', {'schedule': 'cached_schedule_snippet.html', 'term': term})
        except TemplateDoesNotExist:
            pass

    return render(request, 'schedule.html', {'schedule': 'schedule_snippet.html', 'term': term, 'classes': get_classes(),
                                             'tutors': get_tutors(),
                                             'display': request.user.is_staff or Settings.objects.display_tutoring()})


@login_required()
def classes(request):
    term = Settings.objects.term()
    tutors = []
    for hour, hour_name in HOUR_CHOICES:
        tutors_for_hour = []
        tutoring_objs = [t for t in Tutoring.current.all()] + [t for t in ForeignTutoring.current.all()]
        for day, day_name in DAY_CHOICES:
            tutors_for_hour.append(
                sorted(t for t in tutoring_objs
                       if (t.hour_1 == hour and t.day_1 ==day) or (t.hour_2 ==hour and t.day_2 == day)) +
                sorted(itertools.chain.from_iterable(t.profile.classes.all() for t in tutoring_objs
                                                     if (t.hour_1 == hour and t.day_1 == day) or (t.hour_2 == hour and t.day_2 == day))))
        tutors.append((hour_name, tutors_for_hour))

    return render(request, 'classes.html', {'term': term, 'tutors': tutors})


@login_required()
def expanded_schedule(request):
    term = Settings.objects.term()
    tutors = []
    for hour, hour_name in HOUR_CHOICES:
        tutors_for_hour = []
        for day, day_name in DAY_CHOICES:
            if Settings.objects.display_tutoring() or (request.user.is_authenticated and request.user.is_staff):
                tutors_for_hour.append(['{} {}'.format(1, tutor) for tutor in Tutoring.current.filter(best_hour=hour, best_day=day)] +
                                       ['{} {}'.format(1, tutor) for tutor in Tutoring.current.filter(best_hour=str(int(hour)-1), best_day=day)] +
                                       ['{} {}'.format(2, tutor) for tutor in Tutoring.current.filter(second_best_hour=hour, second_best_day=day)] +
                                       ['{} {}'.format(2, tutor) for tutor in Tutoring.current.filter(second_best_hour=str(int(hour)-1), second_best_day=day)] +
                                       ['{} {}'.format(3, tutor) for tutor in Tutoring.current.filter(third_best_hour=hour, third_best_day=day)] +
                                       ['{} {}'.format(3, tutor) for tutor in Tutoring.current.filter(third_best_hour=str(int(hour)-1), third_best_day=day)])
            else:
                tutors_for_hour.append(None)
        tutors.append((hour_name, tutors_for_hour))

    classes = []
    for department, number in zip(Class.DEPT_CHOICES, numbers):
        department, _ = department
        courses = [(cls.course_number, cls.department+cls.course_number)
                   for cls in sorted((c for c in Class.objects.filter(department=department, display=True)
                                      if any(filter(Profile.current, c.profile_set.all()))),
                                     key=lambda c: tuple(int(s) if s.isdigit() else s
                                                         for s in re.search(r'(\d+)([ABCD]?L?)?',
                                                                            c.course_number).groups()))]
        if courses:
            classes.append((department, courses, 'collapse{}'.format(number)))

    return render(request, 'schedule.html', {'term': term, 'classes': classes, 'tutors': tutors,
                                             'display': request.user.is_staff or Settings.objects.display_tutoring()})
def feedback(request):
    return render(request, 'tutoring_feedback.html')

@login_required(login_url='/login')
def tutoring_logging(request):
    c_term = Settings.objects.term()
    tutoring = get_object_or_404(Tutoring, profile=request.user.profile, term=c_term)
    error = None
    classes = None
    confirm = False

    td = (datetime.datetime.now() - tutoring.last_start).seconds
    hours = td // 3600
    if (td // 60) % 60 >= 45:
        hours += 1

    if request.method == "POST":
        if 'sign_in' in request.POST:
            tutoring.is_tutoring = True
            tutoring.last_start = datetime.datetime.now()
            hours = 0
            classes = Class.objects.filter(display=True)
            confirm = True

        elif 'sign_out' in request.POST:
            h = hours
            tutees = int(request.POST['tutees'])
            makeup_t = int(request.POST['makeup_tutoring'])
            makeup_e = int(request.POST['makeup_event'])
            class_ids = request.POST.getlist('subjects')

            if (makeup_t + makeup_e) > hours:
                error = 'Hmm please check your math. According to our records, you have tutored approximately ' + str(
                    hours) + 'hours this session (we round up after 45 minutes).'
                #error = 'apparently, '+str(makeup_t)+' + ' +str(makeup_e) + ' > ' + str(hours)
            else:
                tutoring.is_tutoring = False
                week = c_term.get_week()
                if makeup_e > 0:
                    h -= makeup_e #hours not logged! TODO: email member coord?
                if makeup_t > 0:
                    for i in range(3, week):
                        week_obj = getattr(tutoring, 'week_'+str(i))
                        while week_obj.complete() and h > 0:
                            week_obj.hours += 1
                            h -= 1
                            week_obj.no_makeup = False
                        week_obj.save()
                cur_week = getattr(tutoring, 'week_'+str(week))
                cur_week.hours += h
                cur_week.tutees += tutees
                cur_week.save()
                for s in class_ids:
                    s = int(s)
                    cur_week.classes.add(Class.objects.get(id=s))
                confirm = True

    else:
        if tutoring.is_tutoring:
            if tutoring.last_start.date() != datetime.datetime.now().date():  # midnight passed :P
                error = 'You forgot to sign out of your last tutoring session. Please contact the tutoring chair to have those hours logged'
                tutoring.is_tutoring = False
            else:  # actually is tutoring
                classes = Class.objects.filter(display=True)

    tutoring.save()
    return render(request, 'tutoring_logging.html', {'error': error, 'isTutoring': tutoring.is_tutoring, 'hours': hours, 'classes': classes, 'confirm': confirm})
