from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('web.views',
    url(r'^$', 'home', name='home'),
    url(r'^about/$', 'about'),
    url(r'^awards/$', 'awards'),
    url(r'^candidates/$', 'candidates'),
    url(r'^contact/$', 'officers'),
    url(r'^emcc/$', 'emcc'),
    url(r'^fe/$', 'fe'),
    url(r'^programs/$', 'programs'),
    url(r'^requirements/$', 'requirements'),
    url(r'^tutoring/$', 'tutoring'),

    url(r'^donate/$', 'donate'),
    url(r'^sponsor/$', 'sponsor'),
    url(r'^officers/$', 'officers'),
    url(r'^faculty/$', 'faculty'),
    url(r'^calendar/$', 'room_calendar'),
)

urlpatterns += patterns('main.views',
    url(r'^tutoring_hours/$', 'tutoring_hours'),
    url(r'^houses/$', 'houses'),

    url(r'^profile_requirements/$', 'requirements_view'),
    url(r'^candidate_requirements/$', 'candidates'),
    url(r'^pending_community_service/$', 'pending_community_service'),
    url(r'^active_members/$', 'active_members'),
    url(r'^downloads/$', 'downloads'),

    # url(r'^spreadsheet/$', 'spreadsheet'),
    url(r'^all_profiles/$', 'all_profiles'),
    url(r'^resumes_pdf/$', 'resumes_pdf'),
    url(r'^resumes_word/$', 'resumes_word'),

    url(r'^logout/$', 'logout'),
    url(r'^login/$', 'login'),
    url(r'^profile/$', 'profile_view'),
    url(r'^edit/$', 'edit'),
    url(r'^add/$', 'add'),
    url(r'^register/$', 'register'),
    url(r'^account/$', 'account'),

    url(r'^resume_pdf/$', 'resume_pdf'),
    url(r'^resume_pdf/(?P<id>\d+)$', 'resume_pdf'),
    url(r'^resume_word/$', 'resume_word'),
    url(r'^resume_word/(?P<id>\d+)$', 'resume_word'),
    url(r'^interview/$', 'interview'),
    url(r'^interview/(?P<id>\d+)$', 'interview'),
    url(r'^proof/$', 'proof'),
    url(r'^proof/(?P<id>\d+)$', 'proof'),

    url(r'^add_requirement/$', 'add_requirement'),
)

urlpatterns += patterns('event.views',
    url(r'^events/$', 'events'),
    url(r'^events/manage$', 'manage_events'),
    url(r'^events/(?P<url>\w+)/$', 'event'),
    url(r'^cb_race/$', 'event_redirect', {'event_url': 'cb_race'}),
    url(r'^scholarship/$', 'event_redirect', {'event_url': 'scholarship'}),
    url(r'^rubegoldberg/$', 'event_redirect', {'event_url' : 'RG2016'}),
    url(r'^charitypoker/$', 'event_redirect', {'event_url' : 'CharityPoker'}),
)

urlpatterns += patterns('',
    url(r'^schedule/$', 'tutoring.views.schedule'),
    url(r'^classes/$', 'tutoring.views.classes'),
    url(r'^expanded_schedule/$', 'tutoring.views.expanded_schedule'),
    url(r'^tutoring/feedback/$', 'tutoring.views.feedback'),
    url(r'^tutoring/log_hours/$', 'tutoring.views.tutoring_logging'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
