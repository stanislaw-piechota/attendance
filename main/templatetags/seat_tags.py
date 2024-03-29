from django import template
import mimetypes
from django.shortcuts import HttpResponse
register = template.Library()

def get_row(value, i):
    seats = value.filter(row=i)
    return seats

def get_seat(value, j):
    seat = value.filter(col=j)[0]
    return seat.empty

register.filter(get_row)
register.filter(get_seat)