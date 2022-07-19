from multiprocessing.dummy import Value
from django.shortcuts import render, redirect
from .models import *
from bcrypt import checkpw
from datetime import datetime, timedelta
from .forms import *
from pytz import timezone, UTC

def index(response):
    # user verified
    if response.COOKIES.get('attendance_verified'):
        return redirect("/student")

    # not verified, but sent code
    if response.method == "POST":
        if response.POST.get('code'):
            codes = VerificationCode.objects.all().filter(code=response.POST.get('code'))
            if len(codes):
                id = codes[0].user_id
                user = Student.objects.all().filter(id=id)
                request = redirect("/student")
                request.set_cookie("attendance_verified", str(id), expires=datetime.now()+timedelta(days=400))
                return request
            return render(response, "main/verify.html", {"error": "Kod nie istnieje"})

    return render(response, "main/verify.html", {"error": ""})


def data_verify(data):
    room, row, col, hash = data.split('#')
    room, row, col = int(room), int(row), int(col)

    if row and col:
        checksum = room*row//col
    else:
        checksum = room+2137

    return room, row, col, checkpw(str(checksum).encode(), hash.encode())


def student(response):
    # not verified user
    if not response.COOKIES.get('attendance_verified'):
        return redirect("/")

    # sent form
    if response.method == "POST":
        stud = Student.objects.all().filter(id=response.COOKIES.get('attendance_verified'))[0]
        data = data_verify(response.COOKIES.get('qr_data'))
        stud.room = data[0]
        stud.row = data[1]
        stud.col = data[2]
        stud.last_time = datetime.now()
        stud.save()
        return redirect("/success")

    # user sent QR
    if response.COOKIES.get('qr_data'):
        data = data_verify(response.COOKIES.get('qr_data'))
        if data[3]:
            return render(response, "main/home.html", {"room": data[0], "row": data[1], "col": data[2]})

    return render(response, "main/home.html", {"room": 0, "row": 0, "col": 0})


def success(response):
    if not response.COOKIES.get('attendance_verify'):
        return redirect('/')

    return render(response, "main/success.html", {})


def teacher_login(response):
    if response.session.get('auth') and response.session.get('id'):
        return redirect('/teacher')

    if response.method == "POST":
        if response.POST.get('login') and response.POST.get('pin'):
            try:
                teachers = Teacher.objects.all().filter(login=response.POST.get('login'),
                    pin=int(response.POST.get('pin')))
                if len(teachers) == 1:
                    response.session['auth'] = True
                    response.session['id'] = teachers[0].id
                    return redirect('/teacher')
                raise ValueError
            except Exception as e:
                return render(response, "main/login.html", {"error": "Nieprawidłowy login i/lub PIN"})
        return render(response, "main/login.html", {"error": "Brak danych"})
    return render(response, "main/login.html", {"error": ""})


def teacher(response):
    if not response.session.get('auth') or not response.session.get('id'):
        return redirect('/login')
    
    t = Teacher.objects.filter(id=response.session.get('id'))[0]

    if response.method == "POST" and response.POST.get('logout'):
        response.session['auth'] = False
        response.session['id'] = None
        return redirect('/login')
    elif response.method == "POST" and response.POST.get('update'):
        room, class_name = response.COOKIES.get('room'), response.COOKIES.get('class')
        if class_name != "Klasa":
            t.class_name = class_name
        try:
            if room not in ["Sala", "Brak"]:
                t.room = int(room)
            else:
                raise ValueError
        except Exception as e:
            t.room = 0

        t.save()
        return redirect('/teacher')

    classes = sorted(list(set([student.class_name for student in Student.objects.all()])))
    rooms = sorted(list(set([seat.room for seat in Seat.objects.all()])))
    context = {"teacher": t, "classes": classes, "rooms": rooms}

    if t.class_name != "NO" and t.room:
        all = Student.objects.filter(class_name=t.class_name)
        found = Student.objects.filter(class_name=t.class_name, room=t.room)
        present, absent = [], []
        now = datetime.now()
        start = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, tzinfo=UTC)
        end = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=45, tzinfo=UTC)
        for user in found[::]:
            print(user.last_time)
            if start <= user.last_time <= end:
                present.append(user)
        for user in all:
            if user not in present:
                absent.append(user)
        context['present'] = present
        context['absent'] = absent
    return render(response, "main/teacher.html", context)