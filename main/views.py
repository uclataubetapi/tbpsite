import cStringIO as StringIO
import datetime
import os, re
import time
import zipfile

from django.forms.models import model_to_dict
from django.contrib import auth
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.db.models import Q

from main.models import Profile, Term, Candidate, ActiveMember, House, HousePoints, Settings, MAJOR_CHOICES, PeerTeaching, Requirement
from main.forms import LoginForm, RegisterForm, UserAccountForm, UserPersonalForm, ProfileForm, CandidateForm, MemberForm, ShirtForm, FirstProfileForm, PeerTeachingForm
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


def update_professor_interview_and_resume(candidate):
    if candidate.resume() and candidate.professor_interview and (Settings.objects.term().due_date is None or
                                                                 datetime.date.today() <= Settings.objects.term().due_date):
        candidate.professor_interview_and_resume = True
        candidate.save()


def render_profile_page(request, template, template_args=None):
    """
    Helper function that looks up the links for the profile tabs

    :param request: The request object used to generate this response.
    :param template: The full name of a template to use or sequence of template names.
    :param template_args: Variables to pass to the template
    :returns: Rendered template
    """
    if template_args is None:
        template_args = {}  # if no template_args were passed, initialize to empty dictionary

    tabs = [(reverse('main.views.profile_view'), 'Profile'),  # tuples of the url for the view and the tab label
            (reverse('main.views.edit'), 'Edit Profile'),
            (reverse('main.views.add'), 'Modify Classes'),
            (reverse('main.views.requirements_view'), request.user.profile.get_position_display())]

    template_args['profile_tabs'] = tabs  # add the tab tuples to the variables to pass to the template

    return render(request, template, additional=template_args)  # render the template


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
    user = request.user  # user object associated with the user requesting the webpage
    try:
        profile = user.profile  # lookup profile object associated with the user
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)  # if the profile does not exist, create a user

    # If profile isn't complete, redirect to edit profile page
    if not all([user.email, user.first_name, user.last_name, profile.graduation_term and profile.graduation_term.year]):
        return redirect(edit)

    if profile.position == Profile.CANDIDATE:  # if profile belongs to a candidate, grab information about the candidate
        candidate = profile.candidate

        #Core Requirements
        core_requirements = ((name, 'Completed' if requirement else 'Not Completed') 
                            for name, requirement in candidate.requirements())

        #Peer Teaching Track
        track = (candidate.peer_teaching_track(), 
                'Completed' if candidate.peer_teaching_complete() else 'Not Completed')

        #Event Requirements
        ev_reqs = [] #Format = ['Category', (listOfEvents, pointTotal, categoryPointsNeeded)]
        electiveSum = 0
        for cat in (Requirement.CATEGORY_CHOICES): #cat[0] = number representation, cat[1] = word rep
            # possibleReqs = []
            catReqs = []

            #Generate all attended events in this category
            for r in candidate.event_requirements.all():
                if(r.requirement_choice == cat[0]):
                    catReqs.append(r)

            #Determine which events count for this category (catRegs),
            #and which count for the 'Elective' category
            #NOTE: Gonna find a cool way of making this work later
            #For now a simpler approach of just adding the excess points
            #over the cap to the elective total. This also allows the candidate
            #to not meet the cap precisely (ie have 2 events worth 20 instead
            #of requiring 3 events like 5, 15, 10)
            # candidate.get_reqs_in_cat(cat[1], 0, catReqs, possibleReqs)
            # electiveRecs = [req for req in possibleReqs if req not in catReqs]

            #Sum point totals
            sum = 0
            for req in catReqs:
                sum += req.point_value
            if sum > 20:
                electiveSum += sum-20
                sum -= electiveSum
            ev_reqs.append((cat[1], (catReqs, sum, Requirement.POINTS_NEEDED[cat[1]])))
            
        ev_reqs.append(('Elective', (None, electiveSum, Requirement.POINTS_NEEDED['Elective'])))

        details = None  # extra profile information
    else:  # otherwise the profile belongs to an active member
        ev_reqs = None
        ev_requirement_totals = None # for now until we know how we want to deal with AM's
        track = None
        try:
            am = ActiveMember.objects.get(profile=profile, term=Settings.objects.term)
            core_requirements = ((name, 'Completed' if requirement else 'Not Completed') for name, requirement in
                            ActiveMember.objects.get(profile=profile, term=Settings.objects.term).requirements())
            #track = (am.peer_teaching_track(), 'Completed' if am.peer_teaching_complete() else 'Not Completed')
        
        except ActiveMember.DoesNotExist:
            core_requirements = None
            track = None
            
            

        details = ((active.term, 'Completed' if active.completed else 'In Progress')
                   for active in ActiveMember.objects.filter(profile=profile))

    fields = (  # grab the user/profile information to render
        ('Email', user.email),
        ('First Name', user.first_name),
        ('Middle Name', profile.middle_name),
        ('Last Name', user.last_name),
        ('Nickname', profile.nickname),
        ('House', profile.house),
        ('Gender', profile.get_gender_display()),
        ('Birthday', profile.birthday),
        ('Phone Number', profile.phone_number),
        ('Major', profile.get_major_display()),
        ('Graduation Term', profile.graduation_term),
    )

    return render_profile_page(  # render the profile.html template with these variables
        request, 'profile.html', {
            'user': user, 'profile': profile, 'fields': fields,
            'resume_pdf': time.ctime(os.path.getmtime(profile.resume_pdf.path)) if profile.resume_pdf else None,
            'resume_word': time.ctime(os.path.getmtime(profile.resume_word.path)) if profile.resume_word else None,
            'core_requirements': core_requirements,
            'track': track,
            'ev_reqs': ev_reqs,
            'details': details
        })


@login_required(login_url=login)
def edit(request):
    user = request.user
    profile = user.profile
    first_time = hasattr(profile, 'candidate') and profile.candidate.peer_teaching is None

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
            tutoring_form = TutoringPreferencesForm()
            shirt_form = ShirtForm()
            peer_teaching_form = PeerTeachingForm()
            
    else:
        user_personal_form = UserPersonalForm(request.POST, instance=user)

        if not first_time:
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            valid_forms = [form.is_valid() for form in (user_personal_form, profile_form)]
        else:
            profile_form = FirstProfileForm(request.POST, instance=profile)
            tutoring_form = TutoringPreferencesForm(request.POST)
            shirt_form = ShirtForm(request.POST, instance=profile.candidate)
            peer_teaching_form = PeerTeachingForm(request.POST)
            valid_forms = [form.is_valid() for form in (user_personal_form, profile_form, tutoring_form, shirt_form, peer_teaching_form)]

        if all(valid_forms):
            term, created = Term.objects.get_or_create(quarter=profile_form.cleaned_data['graduation_quarter'],
                                                       year=profile_form.cleaned_data['graduation_year'])

            user_personal_form.save()
            profile.middle_name = user_personal_form.cleaned_data['middle_name']
            profile.graduation_term = term
            profile_form.save()

            if not first_time:
                if profile.position == Profile.CANDIDATE:
                    update_professor_interview_and_resume(profile.candidate)
                return redirect(profile_view)
            else:
                candidate = profile.candidate
                candidate.peer_teaching = PeerTeaching.objects.create(profile=profile, term=Settings.objects.term())
                if peer_teaching_form.cleaned_data['requirement_choice'] == PeerTeaching.TUTORING:
                    candidate.peer_teaching.tutoring = Tutoring.with_weeks(profile=profile, term=Settings.objects.term())
                    tutoring_form = TutoringPreferencesForm(request.POST, instance=candidate.peer_teaching.tutoring)
                    tutoring_form.save()
                    #candidate.peer_teaching.tutoring=candidate.tutoring

                peer_teaching_form = PeerTeachingForm(request.POST, instance=candidate.peer_teaching)
                peer_teaching_form.save()
                
                    
                shirt_form.save()
                return redirect(add)

    if not first_time:
        return render_profile_page(request, 'edit.html',
                                   {'user_personal_form': user_personal_form, 'profile_form': profile_form})
    else:
        return render_profile_page(request, 'first_edit.html',
                                   {'user_personal_form': user_personal_form, 'profile_form': profile_form,
                                    'tutoring_form': tutoring_form, 'shirt_form': shirt_form, 'peer_teaching_form' : peer_teaching_form})


@login_required(login_url=login)
def add(request):
    departments = (department for department, _ in Class.DEPT_CHOICES)
    profile = request.user.profile
    error = None

    if request.method == "POST":
        if 'add' in request.POST:
            dept = request.POST.get('dept')
            cnums = request.POST.get('cnum')

            cnums = cnums.strip()
            if not re.match(r'^[A-Z]*[1-9][0-9]*[A-Z]*(,\s*[A-Z]*[1-9][0-9]*[A-Z]*)*$', cnums):
                error = 'Invalid format for course number. Please use the format in the provided examples.'
            else:
                for cnum in cnums.split(','):
                    profile.classes.add(Class.objects.get_or_create(department=dept, course_number=cnum.strip())[0])
        elif 'remove' in request.POST:
            for cls in request.POST:
                if request.POST[cls] == 'on':
                    dept, cnum = cls.split(' ', 1)

                    try:
                        cls = Class.objects.get(department=dept, course_number=cnum)
                        profile.classes.remove(cls)
                    except Class.DoesNotExist:
                        pass

        else:
            raise ValidationError

    return render_profile_page(request, 'add.html',
                               {'error': error, 'departments': departments, 'classes': profile.classes.all()})


@login_required(login_url=login)
def requirements_view(request):
    profile = request.user.profile

    if profile.position == Profile.CANDIDATE:
        term = Settings.objects.term()
        candidate = profile.candidate

        if request.method == "POST":
            form = CandidateForm(request.POST, request.FILES, instance=candidate)
            if form.is_valid():
                form.save()
                update_professor_interview_and_resume(candidate)

        else:
            form = CandidateForm()

        return render_profile_page(request, 'candidate_requirements.html', {'term': term, 'form': form})

    else:
        term = Settings.objects.signup_term()
        if request.method == "POST":
            member = ActiveMember(profile=profile, term=term)
            member.peer_teaching = PeerTeaching.objects.create(profile=profile, term=Settings.objects.term())
            member_form = MemberForm(request.POST, instance=member)
            tutoring_preferences_form = TutoringPreferencesForm(request.POST)

            valid_forms = [form.is_valid() for form in (member_form, tutoring_preferences_form)]
            if all(valid_forms):
                if member_form.cleaned_data['requirement_choice'] == ActiveMember.TUTORING:
                    member.peer_teaching.requirement_choice = PeerTeaching.TUTORING
                    member.peer_teaching.tutoring = Tutoring.with_weeks(profile=profile, term=term)
                    tutoring_preferences_form = TutoringPreferencesForm(request.POST, instance=member.peer_teaching.tutoring)
                    tutoring_preferences_form.save()

                member.peer_teaching.save()
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
    terms_list = Term.objects.filter(Q(quarter='1') | Q(quarter='3'))

    # def generate_all_req_reports(candidates):
    #     #Generated report will contain 
    #     all_req_reports = []
    #     for candidate in candidates:
    #         req_report = candidate.generate_req_report()
    #         req_report.insert(0, candidate.profile)
    #         all_req_reports.append(req_report)
    #     return all_req_reports

    if request.method == "POST":
        term_id = int(request.POST['term'])
        term = Term.objects.get(id=term_id)
        return render(request, 'all_candidate_requirements.html',
                      {'candidate_list': Candidate.objects.filter(term=term), 'dropdown_term' : term, 'terms': terms_list})
    return render(request, 'all_candidate_requirements.html',
                  {'candidate_list': Candidate.current.order_by('profile'), 'dropdown_term' : Settings.objects.term(),
                  'terms': terms_list})


@staff_member_required
def active_members(request):
    terms_list = Term.objects.filter(Q(quarter='1') | Q(quarter='3'))

    if request.method == "POST":
        term_id = int(request.POST['term'])
        term = Term.objects.get(id=term_id)
        return render(request, 'active_members.html',
                      {'member_list': ActiveMember.objects.filter(term=term, profile__user__is_staff=False),
                       'staff_member_list': ActiveMember.objects.filter(term=term, profile__user__is_staff=True),
                       'dropdown_term' : term, 'terms': terms_list})


    aMembers = ActiveMember.current
    return render(request, 'active_members.html', 
                  {'member_list': aMembers.filter(profile__user__is_staff=False).order_by('profile'),
                   'staff_member_list': aMembers.filter(profile__user__is_staff=True).order_by('profile'),
                   'dropdown_term' : Settings.objects.term(), 'terms': terms_list})


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
    return render(request, 'tutoring_hours.html', {'tutoring_list': Tutoring.current.order_by('profile')})


@staff_member_required
def downloads(request):
    return render(request, 'downloads.html')


@staff_member_required
def all_profiles(request):
    # data = '\n'.join(['First Name,Middle Name,Last Name,Email,Nickname,Gender,Birthday,Phone Number,Major,'
    #                   'Initiation Term,Graduation Term'] +
    #                  [profile.dump() for profile in Profile.objects.all() if profile.user.id != 1])
    # response = HttpResponse(data, content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename=spreadsheet.csv'
    # return response
    prof_list_initial = Profile.objects.order_by("user__last_name")
    profile_list = []
    for prof in prof_list_initial:
        if prof.user.last_name:
            profile_list.append(prof) 
    return render(request, 'user_info_dump.html', {'profile_list': profile_list})

def create_zipfile(filenames):
    buffer = StringIO.StringIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        for _, major in MAJOR_CHOICES:
            z.writestr(zipfile.ZipInfo('resumes/{}/'.format(major)), "")
        for profile, resume in filenames:
            path = 'resumes/{}/{} {}{}'.format(profile.get_major_display(),
                                               profile.user.first_name, profile.user.last_name,
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

        path, ext = os.path.splitext(obj.path)
        content_type = {'.pdf': 'application/pdf', '.doc': 'application/msword', '.jpg': 'image/jpeg',
                        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}[ext.lower()]
        filename = 'filename={}{}'.format(self.field, ext)

        response = HttpResponse(FileWrapper(f), content_type=content_type)
        response['Content-Disposition'] = filename
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

@staff_member_required
def add_requirement(request):
    successC = None
    successD = None
    if request.method=="POST":
       term = Settings.objects.term()
       req = Requirement.current.get(id=request.POST['requirement'])
       successC = "Added Requirement " + str(req) +" to Candidates: "
       successD = "Added Requirement " + str(req) +" to Distinguished Actives: "
       for cand_id in request.POST.getlist('candidate'):
           cand = Candidate.objects.get(id=cand_id)
           try:
               cand.event_requirements.add(req)
           except IntegrityError:
               continue
           successC += str(cand) + " "
       for da_id in request.POST.getlist('da'):
           da = ActiveMember.objects.get(id=da_id)
           try:
               da.event_requirements.add(req)
           except IntegrityError:
               continue
           successD += str(da) + " "
    return render(request, 'add_requirement.html', {'candidate_list': Candidate.current.order_by('profile'),
                                                    'da_list': ActiveMember.current.order_by('profile'),
                                                    'requirement_list': Requirement.current.all(), 
                                                    "successC": successC,
                                                    "successD": successD})
