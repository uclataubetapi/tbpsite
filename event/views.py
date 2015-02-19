from datetime import datetime

from django.shortcuts import redirect, get_object_or_404

from common import render
from event.models import Event
from event.forms import CreateEventForm
from main.models import Settings


MANAGE_ACTIONS = ['Add an Event', 'Edit an Event']

def events(request): 
    today = datetime.today()
    return render(request, 'events.html', 
                  {'upcoming_events': [event for event in Event.objects.filter(end__gt=today).order_by('end')
                                       if event.event_type != Event.SOCIAL or request.user.is_authenticated()],
                   'past_events': [event for event in Event.objects.filter(end__lte=today, term=Settings.objects.term()).order_by('-end')
                                   if event.event_type != Event.SOCIAL or request.user.is_authenticated()]})


def event(request, url):
    get_object_or_404(Event, url=url)
    return render(request, 'event_template.html', {'event': Event.objects.get(url=url)})


def event_redirect(request, event_url):
    return redirect('/events/' + event_url)

def manage_events(request):
    current_action = MANAGE_ACTIONS[0]    

    if request.method == "POST":
#        current_action = int(request.POST['action'])
        create_event_form = CreateEventForm(request.POST)
        if(create_event_form.is_valid()):
            create_event_form.save()
            return render(request, 'manage_events.html', {'current_action' : current_action,
                                                  'actions' : MANAGE_ACTIONS})        
    else:
        create_event_form = CreateEventForm()

    return render(request, 'manage_events.html', {'current_action' : current_action,
                                                  'actions' : MANAGE_ACTIONS,
                                                  'create_event_form': create_event_form})
