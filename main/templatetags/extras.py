from django import template

register = template.Library()

@register.filter
def classname(obj, arg=None):
    classname = obj.__class__.__name__
    return classname if arg is None else arg == classname

@register.filter
def prof_major(profile):
    return profile.get_major_display()

@register.filter
def prof_init_term(profile):
    return profile.initiation_term.__unicode__() if profile.initiation_term else ''

@register.filter
def prof_grad_term(profile):
    return profile.graduation_term.__unicode__() if profile.graduation_term else ''

@register.filter
def cand_get_reqpoints_in_cat(candidate, category):
    return candidate.get_reqpoints_in_cat(category)

@register.filter
def getDictValueForKey(dict, key):
    return dict[key]

@register.filter
def listLength(list):
    return len(list)
