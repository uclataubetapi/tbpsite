from datetime import datetime

from django.shortcuts import redirect, get_object_or_404

from common import render
from event.models import Event


def events(request): 
    today = datetime.today()
    return render(request, 'events.html', 
                  {'upcoming_events': [event for event in Event.objects.filter(end__gt=today).order_by('end')
                                       if event.event_type != Event.SOCIAL or request.user.is_authenticated()],
                   'past_events': [event for event in Event.objects.filter(end__lte=today).order_by('-end')
                                   if event.event_type != Event.SOCIAL or request.user.is_authenticated()]})


def event(request, url):
    get_object_or_404(Event, url=url)
    return render(request, 'event_template.html', {'event': Event.objects.get(url=url)})


def event_redirect(request, event_url):
    return redirect('/events/' + event_url)
