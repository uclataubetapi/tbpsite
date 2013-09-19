import datetime
import re

from django.forms.models import model_to_dict
from django.contrib import auth
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from main.admin import generate_candidate
from main.models import Profile, Term, Candidate, ActiveMember, House, HousePoints, Settings,\
        LoginForm, RegisterForm, UserAccountForm, UserPersonalForm, ProfileForm, CandidateForm, MemberForm,\
        DAY_CHOICES, HOUR_CHOICES
from tbpsite.settings import BASE_DIR
from tutoring.models import Tutoring, Class, Feedback, TutoringPreferencesForm
from common import render

def render_profile_page(request, template, template_args=None, **kwargs):
    if not template_args:
        template_args = {}

    tabs = [ ( reverse('main.views.profile_view'), 'Profile' ),
             ( reverse('main.views.edit'), 'Edit Profile' ),
             ( reverse('main.views.add'), 'Modify Classes' ),
             ( reverse('main.views.requirements'), Profile.objects.get(user=request.user).get_position_display() ) ]

    template_args[ 'profile_tabs' ] = tabs

    return render(request, template, template_args, **kwargs)

class Error:
    def __init__(self):
        self.file_too_big = False
        self.wrong_file_type = False
        self.file_type = []

    def errors(self):
        return [self.file_too_big, self.wrong_file_type]

    def error(self):
        return any(self.errors())

def validate_file(f, mime_types, error):
    ret = True

    if f.multiple_chunks(): # 2.5 MB
        error.file_too_big = True
        ret = False

    if f.content_type not in mime_types:
        error.wrong_file_type = True
        ret = False

    return ret

def write_file(upload, save_path):
    with open(save_path, 'wb+') as f:
        for chunk in upload.chunks():
            f.write(chunk)
    return datetime.datetime.today()

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.cleaned_data['user'])
            return redirect(request.GET.get('next', 'home'))
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('next', 'home'))

@login_required(login_url=login)
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    if not all([user.email, user.first_name, user.last_name, profile.graduation_term and profile.graduation_term.year]):
        return redirect(edit, from_redirect='redirect')

    if profile.position == Profile.CANDIDATE:
        try:
            candidate = Candidate.objects.get(profile=profile)
        except Candidate.DoesNotExist:
            candidate = generate_candidate(profile, Settings.objects.term())
        details = ((name, 'Completed' if requirement else 'Not Completed') 
                for name, requirement in candidate.requirements())
    else:
        details = ((active.term, 'Completed' if active.completed else 'In Progress') for active in ActiveMember.objects.filter(profile=profile))

    return render_profile_page(request, 'profile.html', {'user': user, 'profile': profile, 'details': details})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username, new_password = map(form.cleaned_data.get, ('username', 'new_password'))
            User.objects.create_user(username, password=new_password)
            user = auth.authenticate(username=username, password=new_password)
            auth.login(request, user)
            return redirect(edit, from_redirect='redirect')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required(login_url=login)
def edit(request, from_redirect=''):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    error = Error()

    if request.method != "POST":
        user_account_form = UserAccountForm(instance=user)
        user_personal_form = UserPersonalForm(instance=user)
        profile_dict = model_to_dict(profile)

        try:
            profile_dict.update({
                'graduation_quarter': profile.graduation_term.quarter,
                'graduation_year': profile.graduation_term.year
                })
        except AttributeError:
            pass

        profile_form = ProfileForm(instance=profile, initial=profile_dict)
    else:
        user_account_form = UserAccountForm(request.POST, instance=user)
        user_personal_form = UserPersonalForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        valid_forms = [form.is_valid() for form in (user_account_form, user_personal_form, profile_form)]

        if all(valid_forms):
            term, created = Term.objects.get_or_create(quarter=profile_form.cleaned_data['graduation_quarter'], 
                    year=profile_form.cleaned_data['graduation_year'])

            resume_pdf = None
            resume_word = None

            pdf = ('application/pdf', 'application/force-download')
            word = ('application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

            if 'resume_pdf' in request.FILES:
                resume_pdf = request.FILES['resume_pdf']
                if validate_file(resume_pdf, pdf, error):
                    profile.resume_pdf = write_file(resume_pdf, '{}/resumes_pdf/{}'.format(BASE_DIR, user.id))
                else:
                    error.file_type.append('Resume (pdf)')

            if 'resume_word' in request.FILES:
                resume_word = request.FILES['resume_word']
                if validate_file(resume_word, word, error):
                    profile.resume_word = write_file(resume_word, '{}/resumes_word/{}'.format(BASE_DIR, user.id))
                else:
                    error.file_type.append('Resume (word)')

            if not error.error():
                if user_account_form.cleaned_data['new_password']:
                    user.set_password(user_account_form.cleaned_data['new_password'])

                user_account_form.save()
                user_personal_form.save()
                profile.graduation_term = term
                profile_form.save()
                return redirect(profile_view)

    classes = profile.classes.all()

    return render_profile_page(request, 'edit.html', {
        'user_account_form': user_account_form, 'user_personal_form': user_personal_form, 'profile_form': profile_form, 
        'from_redirect': from_redirect, 'user': user, 'profile': profile})

@login_required(login_url=login)
def add(request):
    departments = (department for department, _ in Class.DEPT_CHOICES)
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        dept = request.POST.get('dept')
        cnums = request.POST.get('cnum')
        if cnums:
            for cnum in cnums.split(','):
                profile.classes.add(Class.objects.get_or_create(department=dept, course_number=cnum.strip())[0])
        else:
            for cls in request.POST:
                if request.POST[cls] == 'on':
                    dept, cnum = cls.split()
                    try:
                        cls = Class.objects.get(department=dept, course_number=cnum)
                        profile.classes.remove(cls)
                    except Class.DoesNotExist:
                        pass
    
    return render_profile_page(request, 'add.html', {'departments': departments, 'classes': profile.classes.all()})

@login_required(login_url=login)
def resume_pdf(request):
    user = request.user
    try:
        f = open(BASE_DIR + '/resumes_pdf/' + str(user.id))
        response = HttpResponse(FileWrapper(f), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=resume.pdf'
        return response
    except IOError:
        return redirect_next(request)

@login_required(login_url=login)
def resume_word(request):
    user = request.user
    try:
        f = open(BASE_DIR + '/resumes_word/' + str(user.id))
        response = HttpResponse(FileWrapper(f), content_type='application/msword')
        response['Content-Disposition'] = 'attachment; filename=resume.doc'
        return response
    except IOError:
        return redirect_next(request)

@login_required(login_url=login)
def interview(request):
    user = request.user
    response = None
    try:
        f = open(BASE_DIR + '/interviews/' + str(user.id))
        response = HttpResponse(FileWrapper(f), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=interview.pdf'
        return response
    except IOError:
        return redirect_next(request)

@login_required(login_url=login)
def requirements(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    term = Settings.objects.term()

    if profile.position == Profile.CANDIDATE:
        candidate = Candidate.objects.get(profile=profile)
        tutoring = candidate.tutoring

        if request.method == "POST":
            candidate_form = CandidateForm(request.POST, request.FILES, instance=candidate)
            if tutoring is None:
                tutoring_preferences_form = TutoringPreferencesForm(request.POST)

            if candidate_form.is_valid and (tutoring is not None or tutoring_preferences_form.is_valid()):
                if tutoring is None:
                    candidate.tutoring = Tutoring.with_weeks(profile, term)
                    tutoring_preferences_form = TutoringPreferencesForm(request.POST, instance=candidate.tutoring)
                    tutoring_preferences_form.save()

                candidate_form.save()
                tutoring_preferences_form = None

        else:
            candidate_form = CandidateForm(instance=candidate)
            if tutoring is None:
                tutoring_preferences_form = TutoringPreferencesForm()
            else:
                tutoring_preferences_form = None

        return render_profile_page(request, 'candidate_requirements.html', 
                {'term': term, 'candidate_form': candidate_form, 
                    'tutoring_preferences_form': tutoring_preferences_form})
                
    else:
        if request.method == "POST":
            member_form = MemberForm(request.POST)
            tutoring_preferences_form = TutoringPreferencesForm(request.POST)

            valid_forms = [form.is_valid() for form in (candidate_form, tutoring_preferences_form)]
            if all(valid_forms):
                member = ActiveMember.objects.create(profile=profile, term=term)
                member_form = MemberForm(request.POST, instance=member)
                member_form.save()

                if candidate_form.cleaned_data['requirement_choice'] == ActiveMember.TUTORING:
                    tutoring = Tutoring.with_weeks(profile=profile, term=term)
                    tutoring_preferences_form = TutoringPreferencesForm(request.POST)
                    tutoring_preferences_form.save()

                member_form = None
                tutoring_preferences_form = None

        else:
            member_form = MemberForm()
            tutoring_preferences_form = TutoringPreferencesForm()

        return render_profile_page(request, 'member_requirements.html', 
                {'term': term, 'requirement': member.get_requirement_choice_display(), 
                    'member_form': member_form, 'tutoring_preferences_form': tutoring_preferences_form})

@staff_member_required
def candidates(request):
    return render(request, 'all_candidate_requirements.html', {'candidate_list': Candidate.current.order_by('profile')})

@staff_member_required
def active_members(request):
    return render(request, 'active_members.html', {'member_list': ActiveMember.current.order_by('profile')})

@staff_member_required
def tutoring_hours(request):
    return render(request, 'tutoring_hours.html', {'tutoring_list': Tutoring.objects.order_by('profile')})

@staff_member_required
def tutoring_feedback(request):
    return render(request, 'tutoring_feedback.html', {'tutoring_feedback': Feedback.objects.order_by('-timestamp')})

def houses(request):
    term = Settings.objects.term()
    house_points = [HousePoints.objects.get_or_create(house=house, term=term)[0] for house in House.objects.all()]
    return render(request, 'houses.html', {'houses': house_points})

@staff_member_required
def downloads(request):
    return render(request, 'downloads.html')

@staff_member_required
def spreadsheet(request):
    data = '\n'.join(['First Name,Middle Name,Last Name,Email,Nickname,Gender,Birthday,Phone Number,Major,Initiation Term,Graduation Term'] + 
            [profile.dump() for profile in Profile.objects.all() if profile.user.id != 1])
    response = HttpResponse(data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=spreadsheet.csv'
    return response

@staff_member_required
def preferences(request):
    term = Settings.objects.term()
    tutors = (tutoring.profile for tutoring in Tutoring.objects.filter(term=term))
    return render(request, 'preferences.html', {'tutors': tutors})
