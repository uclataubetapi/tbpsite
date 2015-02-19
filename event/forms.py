from django import forms
from django.forms import ModelForm
from event.models import Event
from main.models import Profile


class CreateEventForm(ModelForm):
    name = forms.CharField(required=True, label="Event Name")
    description = forms.CharField(required=True, label="Event Description")
    start = forms.DateTimeField(label="Start Date/Time", widget=forms.DateTimeInput, 
                                help_text="(mm/dd/yyyy hh:mm:ss)")
    end = forms.DateTimeField(label="End Date/Time", widget=forms.DateTimeInput, 
                                help_text="(mm/dd/yyyy hh:mm:ss)")
    

    class Meta:
        model = Event
        fields = ['name', 'term', 'description', 'start', 'end', 'location', 'event_type', 'image']
