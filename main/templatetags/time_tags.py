from django import template
register = template.Library()

def hour(value):
    append = ''
    if value.minute > 15:
        append = ' (sp)'
    return value.strftime('%H:%M:%S')+append

register.filter('hour', hour)