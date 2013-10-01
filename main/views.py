import cStringIO as StringIO
import datetime
import os
import time
import zipfile

from django.forms.models import model_to_dict
from django.contrib import auth
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.utils.decorators import method_decorator

from main.models import Profile, Term, Candidate, ActiveMember, House, HousePoints, Settings, MAJOR_CHOICES,\
    LoginForm, RegisterForm, UserAccountForm, UserPersonalForm, ProfileForm, CandidateForm, MemberForm, ShirtForm,\
    FirstProfileForm
from tutoring.models import Tutoring, Class, TutoringPreferencesForm
from common import render

MAJOR_MAPPING = {
    '0': 'AeroE',
    '1': 'BE',
    '2': 'ChemE',
    '3': 'CivilE',
    '4': 'CS',
    '5': 'CSE',
    '6': 'EE',
    '7': 'MatE',
    '8': 'MechE'
}


def render_profile_page(request, template, template_args=None):
    if not template_args:
        template_args = {}

    tabs = [(reverse('main.views.profile_view'), 'Profile'),
            (reverse('main.views.edit'), 'Edit Profile'),
            (reverse('main.views.add'), 'Modify Classes'),
            (reverse('main.views.requirements'), request.user.profile.get_position_display())]

    template_args['profile_tabs'] = tabs

    return render(request, template, additional=template_args)


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


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username, new_password = map(form.cleaned_data.get, ('username', 'new_password'))
            user = User.objects.create_user(username, password=new_password)
            auth.login(request, auth.authenticate(username=username, password=new_password))
            profile = Profile.objects.create(user=user)
            Candidate.objects.create(profile=profile, term=Settings.objects.term())
            return redirect(edit)
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def houses(request):
    term = Settings.objects.term()
    house_points = [HousePoints.objects.get_or_create(house=house, term=term)[0] for house in House.objects.all()]
    return render(request, 'houses.html', {'houses': house_points})


@login_required(login_url=login)
def account(request):
    if request.method == "POST":
        form = UserAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            if form.cleaned_data['new_password']:
                request.user.set_password(form.cleaned_data['new_password'])
            form.save()
    form = UserAccountForm(instance=request.user)
    return render(request, 'account.html', {'form': form})


@login_required(login_url=login)
def profile_view(request):
    user = request.user
    profile = user.profile
    if not all([user.email, user.first_name, user.last_name, profile.graduation_term and profile.graduation_term.year]):
        return redirect(edit)

    if profile.position == Profile.CANDIDATE:
        candidate = profile.candidate
        requirements = ((name, 'Completed' if requirement else 'Not Completed')
                        for name, requirement in candidate.requirements())
        details = None
    else:
        try:
            requirements = ((name, 'Completed' if requirement else 'Not Completed') for name, requirement in
                            ActiveMember.objects.get(profile=profile, term=Settings.objects.term).requirements())
        except ActiveMember.DoesNotExist:
            requirements = None
        details = ((active.term, 'Completed' if active.completed else 'In Progress') 
                   for active in ActiveMember.objects.filter(profile=profile))

    fields = (
        ('Email', user.email),
        ('First Name', user.first_name),
        ('Middle Name', profile.middle_name),
        ('Last Name', user.last_name),
        ('Nickname', profile.nickname),
        ('Gender', profile.get_gender_display()),
        ('Birthday', profile.birthday),
        ('Phone Number', profile.phone_number),
        ('Major', profile.get_major_display()),
        ('Graduation Term', profile.graduation_term),
    )

    return render_profile_page(
        request, 'profile.html', {
            'user': user, 'profile': profile, 'fields': fields,
            'resume_pdf': time.ctime(os.path.getmtime(profile.resume_pdf.path)) if profile.resume_pdf else None,
            'resume_word': time.ctime(os.path.getmtime(profile.resume_word.path)) if profile.resume_word else None,
            'requirements': requirements, 'details': details
        })


@login_required(login_url=login)
def edit(request):
    user = request.user
    profile = user.profile
    first_time = profile.candidate and profile.candidate.tutoring is None

    if request.method != "POST":
        personal_dict = model_to_dict(user)
        personal_dict['middle_name'] = profile.middle_name
        user_personal_form = UserPersonalForm(instance=user, initial=personal_dict)

        profile_dict = model_to_dict(profile)
        if profile.graduation_term is not None:
            profile_dict.update({
                'graduation_quarter': profile.graduation_term.quarter,
                'graduation_year': profile.graduation_term.year
            })

        if not first_time:
            profile_form = ProfileForm(initial=profile_dict)
        else:
            profile_form = FirstProfileForm(initial=profile_dict)
            form = TutoringPreferencesForm()
            shirt_form = ShirtForm()

    else:
        user_personal_form = UserPersonalForm(request.POST, instance=user)

        if not first_time:
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            valid_forms = [form.is_valid() for form in (user_personal_form, profile_form)]
        else:
            profile_form = FirstProfileForm(request.POST, instance=profile)
            candidate = profile.candidate
            candidate.tutoring = Tutoring.with_weeks(profile=profile, term=Settings.objects.term())
            form = TutoringPreferencesForm(request.POST, instance=candidate.tutoring)
            shirt_form = ShirtForm(request.POST, instance=candidate)
            valid_forms = [form.is_valid() for form in (user_personal_form, profile_form, form, shirt_form)]

        if all(valid_forms):
            term, created = Term.objects.get_or_create(quarter=profile_form.cleaned_data['graduation_quarter'],
                                                       year=profile_form.cleaned_data['graduation_year'])

            user_personal_form.save()
            profile.middle_name = user_personal_form.cleaned_data['middle_name']
            profile.graduation_term = term
            profile_form.save()

            if first_time:
                form.save()
                shirt_form.save()

            return redirect(add)

    if not first_time:
        return render_profile_page(request, 'edit.html',
                                   {'user_personal_form': user_personal_form, 'profile_form': profile_form})
    else:
        return render_profile_page(request, 'first_edit.html',
                                   {'user_personal_form': user_personal_form, 'profile_form': profile_form,
                                    'form': form, 'shirt_form': shirt_form})


@login_required(login_url=login)
def add(request):
    departments = (department for department, _ in Class.DEPT_CHOICES)
    profile = request.user.profile

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
def requirements(request):
    profile = request.user.profile
    term = Settings.objects.term()

    if profile.position == Profile.CANDIDATE:
        candidate = profile.candidate

        if request.method == "POST":
            form = CandidateForm(request.POST, request.FILES, instance=candidate)
            if form.is_valid():
                form.save()

        else:
            form = CandidateForm()

        return render_profile_page(request, 'candidate_requirements.html', {'term': term, 'form': form})
                
    else:
        if request.method == "POST":
            member = ActiveMember(profile=profile, term=term)
            member_form = MemberForm(request.POST, instance=member)
            tutoring_preferences_form = TutoringPreferencesForm(request.POST)

            valid_forms = [form.is_valid() for form in (member_form, tutoring_preferences_form)]
            if all(valid_forms):
                if member_form.cleaned_data['requirement_choice'] == ActiveMember.TUTORING:
                    member.tutoring = Tutoring.with_weeks(profile=profile, term=term)
                    tutoring_preferences_form = TutoringPreferencesForm(request.POST)
                    tutoring_preferences_form.save()

                member_form.save()
                member_form = None
                tutoring_preferences_form = None

        else:
            try:
                member = ActiveMember.objects.get(profile=profile, term=term)
                member_form = None
                tutoring_preferences_form = None
            except ActiveMember.DoesNotExist:
                member = None
                member_form = MemberForm()
                tutoring_preferences_form = TutoringPreferencesForm()

        return render_profile_page(
            request, 'member_requirements.html', {
                'term': term, 'requirement': member.get_requirement_choice_display() if member else '',
                'member_form': member_form, 'tutoring_preferences_form': tutoring_preferences_form
            })


@staff_member_required
def candidates(request):
    return render(request, 'all_candidate_requirements.html', {'candidate_list': Candidate.current.order_by('profile')})


@staff_member_required
def active_members(request):
    return render(request, 'active_members.html', {'member_list': ActiveMember.current.order_by('profile')})


@staff_member_required
def pending_community_service(request):
    if request.method == "POST":
        for id in request.POST:
            if request.POST[id] == 'on':
                Candidate.objects.filter(id=id).update(community_service=1)
    return render(
        request, 'pending_community_service.html', {
            'candidates': [candidate for candidate in
                           Candidate.objects.filter(term=Settings.objects.term, community_service=0).order_by('profile')
                           if not candidate.community_service_complete() and candidate.community_service_proof]
        })


@staff_member_required
def tutoring_hours(request):
    return render(request, 'tutoring_hours.html', {'tutoring_list': Tutoring.objects.order_by('profile')})

@staff_member_required
def downloads(request):
    return render(request, 'downloads.html')


@staff_member_required
def spreadsheet(request):
    data = '\n'.join(['First Name,Middle Name,Last Name,Email,Nickname,Gender,Birthday,Phone Number,Major,'
                      'Initiation Term,Graduation Term'] +
                     [profile.dump() for profile in Profile.objects.all() if profile.user.id != 1])
    response = HttpResponse(data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=spreadsheet.csv'
    return response


def create_zipfile(filenames):
    buffer = StringIO.StringIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        for _, major in MAJOR_CHOICES:
            z.writestr(zipfile.ZipInfo('resumes/{}/'.format(major)), "")
        for profile, resume in filenames:
            date_string = datetime.datetime.fromtimestamp(os.path.getmtime(resume)).strftime('%Y%m')
            path = 'resumes/{}/{}{}_{}{}{}'.format(profile.get_major_display(),
                                                   date_string, MAJOR_MAPPING[profile.major],
                                                   profile.user.first_name[0], profile.user.last_name,
                                                   os.path.splitext(resume)[1])
            z.write(resume, path)

    response = HttpResponse(buffer.getvalue(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=resumes.zip'
    return response


@staff_member_required
def resumes_pdf(request):
    resumes = [(profile, profile.resume_pdf.path) for profile in Profile.objects.all() if profile.resume_pdf]
    return create_zipfile(resumes)


@staff_member_required
def resumes_word(request):
    resumes = [(profile, profile.resume_word.path) for profile in Profile.objects.all() if profile.resume_word]
    return create_zipfile(resumes)


class FileView(View):

    field = ''

    @method_decorator(login_required(login_url=login))
    def get(self, request, *args, **kwargs):

        obj = self.get_object(request, kwargs.get('id'))
        if not obj:
            raise Http404

        try:
            f = open(obj.path)
        except IOError:
            raise Http404

        response = HttpResponse(FileWrapper(f), content_type='application/pdf')
        response['Content-Disposition'] = 'filename={}.pdf'.format(self.field)
        return response

    def get_object(self, request, id):
        raise NotImplementedError


class ProfileFileView(FileView):

    def get_object(self, request, id):
        if not id:
            return getattr(request.user.profile, self.field)
        else:
            if not request.user.is_staff:
                raise Http404
            return getattr(get_object_or_404(Profile, id=id), self.field)


class CandidateFileView(FileView):

    def get_object(self, request, id):
        if not id:
            return getattr(get_object_or_404(Candidate, profile=request.user.profile), self.field)
        else:
            if not request.user.is_staff:
                raise Http404
            return getattr(get_object_or_404(Candidate, id=id), self.field)

resume_pdf = ProfileFileView.as_view(field='resume_pdf')
resume_word = ProfileFileView.as_view(field='resume_word')
interview = CandidateFileView.as_view(field='professor_interview')
proof = CandidateFileView.as_view(field='community_service_proof')
