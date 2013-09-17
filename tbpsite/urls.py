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

    url(r'^officers/$', 'officers'),
    url(r'^faculty/$', 'faculty'),
    url(r'^feedback/$', 'feedback'),
)

urlpatterns += patterns('main.views',
    url(r'^tutoring_hours/$', 'tutoring_hours'),
    url(r'^tutoring_feedback/$', 'tutoring_feedback'),
    url(r'^houses/$', 'houses'),

    url(r'^candidate_requirements/$', 'candidates'),
    url(r'^active_members/$', 'active_members'),
    url(r'^preferences/$', 'preferences'),
    url(r'^downloads/$', 'downloads'),
    url(r'^spreadsheet/$', 'spreadsheet'),

    url(r'^logout/$', 'logout'),
    url(r'^login/$', 'login'),
    url(r'^profile/$', 'profile_view'),
    url(r'^edit/(?P<from_redirect>\w+?)$', 'edit'),
    url(r'^edit/$', 'edit'),
    url(r'^add/$', 'add'),
    url(r'^register/$', 'register'),

    url(r'^resume_pdf/$', 'resume_pdf'),
    url(r'^resume_word/$', 'resume_word'),
    url(r'^interview/$', 'interview'),
)

urlpatterns += patterns('event.views',
    url(r'^events/$', 'events'),
    url(r'^events/(?P<url>\w+)/$', 'event'),
    url(r'^cb_race/$', 'event_redirect', {'event_url': 'cb_race'}),
    url(r'^scholarship/$','event_redirect', {'event_url': 'scholarship'}),
)

urlpatterns += patterns('',
    url(r'^schedule/$', 'tutoring.views.schedule'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
