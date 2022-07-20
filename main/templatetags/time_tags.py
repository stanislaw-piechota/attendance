from django import template
register = template.Library()

def hour(value):
    append = ''
    if value.minute > 15:
        append = ' (sp)'
    return value.strftime('%H:%M:%S')+append

def hour_teacher(value):
    return value.strftime('%H:%M:%S')

def obscure(value):
    return f'{str(value)[0]}***{str(value)[4]}'

register.filter('hour', hour)
register.filter('hour_teacher', hour_teacher)
register.filter('obscure', obscure)