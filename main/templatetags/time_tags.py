from django import template
register = template.Library()

def hour(value):
    return value.strftime('%Y.%m.%d %H:%M:%S')

register.filter('hour', hour)