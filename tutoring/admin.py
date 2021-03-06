from django.contrib import admin

from tutoring.models import *
from points import MIN_TUTORING_HOURS


class ClassAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'department', 'display')
    list_editable = ('display',)
    list_filter = ('display',)


class TutoringAdmin(admin.ModelAdmin):
    fields = ('day_1', 'hour_1', 'day_2', 'hour_2', 'best_day', 'best_hour', 
              'second_best_day', 'second_best_hour', 'third_best_day', 'third_best_hour', 'frozen', 'hidden')
    list_display = ('__unicode__', 'day_1', 'hour_1', 'day_2', 'hour_2', 'best_day', 'best_hour', 
                    'second_best_day', 'second_best_hour', 'third_best_day', 'third_best_hour', 'frozen')
    list_editable = ('day_1', 'hour_1', 'day_2', 'hour_2')
    actions = ('import_tutoring_times',)

    def import_tutoring_times(self, request, queryset):
        for tutoring in queryset:
            tutoring.day_1 = tutoring.day_2 = tutoring.best_day
            tutoring.hour_1 = tutoring.best_hour
            tutoring.hour_2 = str(int(tutoring.hour_1) + 1)
            tutoring.save()


class ForeignTutoringAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'day_1', 'hour_1', 'day_2', 'hour_2')
    list_editable = ('day_1', 'hour_1', 'day_2', 'hour_2')
    filter_horizontal = ('classes',)


class WeekAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'term', 'day_1', 'hour_1', 'day_2', 'hour_2', 'hours', 'tutees')
    list_editable = ('hours', 'tutees')
    actions = ('fill_hours',)

    def fill_hours(self, request, queryset):
        queryset.update(hours=MIN_TUTORING_HOURS)

admin.site.register(Class, ClassAdmin)
admin.site.register(Tutoring, TutoringAdmin)
admin.site.register(ForeignTutoring, ForeignTutoringAdmin)
admin.site.register(Week3, WeekAdmin)
admin.site.register(Week4, WeekAdmin)
admin.site.register(Week5, WeekAdmin)
admin.site.register(Week6, WeekAdmin)
admin.site.register(Week7, WeekAdmin)
admin.site.register(Week8, WeekAdmin)
admin.site.register(Week9, WeekAdmin)
