#!/usr/bin/env python

from django.shortcuts import render as django_render

from event.models import Event
from main.models import Settings

def render(request, template_name, additional=None):
    dictionary = {'user': request.user, 'next': request.path, 
            'events': Event.objects.filter(dropdown=True),
            'eligibility_list': Settings.objects.get_eligibility_list().url}
    if additional is not None:
        dictionary.update(additional)
    return django_render(request, template_name, dictionary)

