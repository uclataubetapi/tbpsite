from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.mail import send_mail

from main.models import *


class MyUserAdmin(UserAdmin):
    actions = ('create_profile', 'reset_password', 'add_staff', 'remove_staff', 'clear_groups')

    def __init__( self, *args, **kwargs ):
        super( UserAdmin, self ).__init__( *args, **kwargs )
        self.list_display += ( 'date_joined', )

    def create_profile(self, request, queryset):
        for user in queryset:
            Profile.objects.create(user=user, position=Profile.MEMBER)

    def reset_password(self, request, queryset):
        for user in queryset:
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            user.email_user(
                'TBP Account Password Reset',
                'Username: %s\n'
                'Password: %s\n'
                '\n'
                'Please change your password and update your information so we can keep the resumes we send out up to date.\n'
                '\n'
                'Webmaster - Tau Beta Pi\n'
                'UCLA - CA Epsilon\n' % (user.get_username(), password),
                'webmaster@tbp.seas.ucla.edu'
            )

        send_mail( 'TBP Password Reset Accounting', 
                'The following users had their passwords reset:\n\n%s' %
                    '\n'.join( [ user.get_username() for user in queryset ] ),
                'webmaster@tbp.seas.ucla.edu', [ 'webmaster@tbp.seas.ucla.edu' ] )

    def add_staff(self, request, queryset):
        queryset.update(is_staff=True)

    def remove_staff(self, request, queryset):
        queryset.update(is_staff=False)

    def clear_groups(self, request, queryset):
        for user in queryset:
            user.groups.clear()


class HousePointsAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'term', 'professor_interview_and_resume', 'other')
    list_editable = ('professor_interview_and_resume', 'other')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'position', 'house', 'major',
                    'initiation_term', 'graduation_term', 'resume_pdf', 'resume_word')
    list_filter = ('position',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    actions = ('create_candidate', 'create_active_member', 'promote_candidate')
    filter_horizontal = ('classes',)

    def create_candidate(self, request, queryset):
        term = Settings.objects.term()
        if term is None:
            self.message_user(request, 'Current term not set')

        # check for errors, all or nothing
        for profile in queryset:
            if profile.position == '1':
                self.message_user(request, '{} is already a member'.format(profile))
                return

            if hasattr(profile, 'candidate'):
                self.message_user(request, '{} is already a candidate'.format(profile))
                return

        for profile in queryset:
            profile.candidate = Candidate.objects.create(profile=profile, term=Settings.objects.term())
            profile.save()

    def create_active_member(self, request, queryset):
        term = Settings.objects.term()
        if term is None:
            self.message_user(request, 'Current term not set')
            return

        for profile in queryset:
            if ActiveMember.objects.filter(profile=profile, term=Settings.objects.term).count():
                self.message_user(request, '{} is already an active member for the term'.format(profile))
                return

        for profile in queryset:
            queryset.update(candidate=Candidate(profile=profile, term=Settings.objects.term))

    def promote_candidate(self, request, queryset):
        queryset.update(position=Profile.MEMBER)


class CandidateAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'term', 'shirt_size', 'bent_polish', 'candidate_quiz', 'quiz_first_try', 'candidate_meet_and_greet',
                     'community_service', 'initiation_fee', 'engineering_futures', 'candidate_sorting')
    list_editable = ('bent_polish', 'candidate_quiz', 'quiz_first_try', 'candidate_meet_and_greet',
                     'community_service', 'initiation_fee', 'engineering_futures', 'candidate_sorting')
    actions = ('create_candidate', 'create_active_member', 'promote_candidate')

    def promote_candidate(self, request, queryset):
        #queryset.update(position__member=Profile.MEMBER)
        for cand in queryset:
            cand.profile.position = Profile.MEMBER
            cand.profile.save()
            cand.save()

class ActiveMemberAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'term', 'requirement_choice', 'requirement_complete')
    list_editable = ('requirement_choice', 'requirement_complete')


class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'dept', 'chapter', 'graduation', 'link')


class SettingsAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'term', 'signup_term', 'display_all_terms', 'display_tutoring', 'registration_code')
    list_editable = ('term', 'signup_term', 'display_all_terms', 'display_tutoring', 'registration_code')


class OfficerAdmin(admin.ModelAdmin):
    list_display = ('position', 'rank', 'mail_alias', 'list_profiles')
    filter_horizontal = ('profile',)

class PeerAdmin(admin.ModelAdmin):
    list_display = ('profile', 'requirement_choice', 'academic_outreach_complete', 'tutoring')
    list_editable = ('requirement_choice', 'academic_outreach_complete')

class RequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'requirement_choice', 'point_value', 'term')
    list_editable = ('requirement_choice', 'point_value')
    
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(Term)
admin.site.register(Settings, SettingsAdmin)
admin.site.register(HousePoints, HousePointsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(ActiveMember, ActiveMemberAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Officer, OfficerAdmin)
admin.site.register(PeerTeaching, PeerAdmin)
admin.site.register(Requirement, RequirementAdmin)
