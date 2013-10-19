import os

from django.template import Context, Template
from django.core.cache import cache
from django.core.management.base import NoArgsCommand

from main.models import Settings
from tbpsite.settings import BASE_DIR
from tutoring.views import get_classes, get_tutors


class Command(NoArgsCommand):
    
    def handle_noargs(self, *args, **kwargs):
        term = Settings.objects.term()
        t = Template(open(os.path.join(BASE_DIR, 'templates', 'schedule_snippet.html')).read())
        c = Context({'term': term, 'classes': get_classes(), 'tutors': get_tutors(), 'display': True})
        open(os.path.join(BASE_DIR, 'cached_templates', 'cached_schedule_snippet.html'), 'w').write(t.render(c))
        cache.clear()
