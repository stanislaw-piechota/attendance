from django.shortcuts import render, redirect
from .models import *
from .commands import decrypt
from datetime import datetime, timedelta
from .forms import *

def student(response):
    if not response.COOKIES.get('attendance_verified'):
        return redirect('/')

    try:
        error=None
        student = Student.objects.filter(id=int(response.COOKIES.get('attendance_verified')))[0]
        room = int(response.GET.get('room'))
        row = int(response.GET.get('row'))
        col = int(response.GET.get('col'))
        checksum = response.GET.get('checksum')

        if decrypt(checksum) == f'{room}/{row}/{col}':
            student.room, student.row, student.col = room, row, col
            student.last_time = datetime.now()
            student.save()
            return render(response, "main/home.html", {"room": room, "row":row, "col":col})
        else:
            raise ValueError

    except:
        error = "Nieprawidłowe dane"

    return render(response, "main/error.html", {"error": error})

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
                request = redirect("/success")
                request.set_cookie("attendance_verified", str(id), expires=datetime.now()+timedelta(days=400))
                return request
            return render(response, "main/verify.html", {"error": "Kod nie istnieje"})

    return render(response, "main/verify.html", {"error": ""})


def success(response):
    if not response.COOKIES.get('attendance_verified'):
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
                dup_teachers = Teacher.objects.filter(room=t.room)
                for teach in dup_teachers:
                    teach.room = 0
                    teach.save()
            else:
                raise ValueError
        except Exception as e:
            t.room = 0
        t.last_activity = datetime.now()

        t.save()
        return redirect('/teacher')
    elif response.method == "POST" and response.POST.get('master'):
        return redirect('/headmaster')

    classes = sorted(list(set([student.class_name for student in Student.objects.all()])))
    rooms = sorted(list(set([seat.room for seat in Seat.objects.all()])))
    context = {"teacher": t, "classes": classes, "rooms": rooms}

    if t.class_name != "NO" and t.room:
        all = Student.objects.filter(class_name=t.class_name)
        found = Student.objects.filter(class_name=t.class_name, room=t.room)
        present, absent = [], []
        now = datetime.now()
        start = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour)
        end = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=45)
        for user in found[::]:
            print(start, user.last_time, end)
            if start <= user.last_time <= end:
                present.append(user)
        for user in all:
            if user not in present:
                absent.append(user)
        context['present'] = present
        context['absent'] = absent
        if response.COOKIES.get('simple-view') == 'true':
            context['simple'] = True
        else:
            context['simple'] = False
            seats = Seat.objects.filter(room=t.room)
            rows, cols = [seat.row for seat in seats], [seat.col for seat in seats]
            context['seats'] = seats
            context['rows'] = reversed(range(1, max(rows)+1))
            context['cols'] = range(1, max(cols)+1)
    return render(response, "main/teacher.html", context)


def master(response):
    if not response.session.get('auth') or not response.session.get('id'):
        return redirect('/login')

    t = Teacher.objects.filter(id=int(response.session.get('id')))[0]
    if not t.master:
        return redirect('/teacher')

    if response.method == "POST":
        if response.POST.get('logout'):
            response.session['auth'] = False
            response.session['id'] = None
            return redirect('/login')
        elif response.POST.get('master'):
            return redirect('/teacher')
        elif response.POST.get('search'):
            return redirect('/headmaster')

    classes = sorted(list(set([student.class_name for student in Student.objects.all()])))
    context = {
        "teacher": t,
        "classes": classes,
        "students": Student.objects.all(),
        "teachers": Teacher.objects.all()
    }
    return render(response, 'main/master.html', context)

def user_s(response, full_name):
    if not response.session.get('auth') or not response.session.get('id'):
        return redirect('/../../login')

    t = Teacher.objects.filter(id=int(response.session.get('id')))[0]
    if not t.master:
        return redirect('/../../teacher')

    if response.method == "POST":
        if response.POST.get('logout'):
            response.session['auth'] = False
            response.session['id'] = None
            return redirect('/../../login')
        elif response.POST.get('master'):
            return redirect('/../../teacher')
        elif response.POST.get('panel'):
            return redirect('/../../headmaster')

    data = full_name.split(' ')
    if len(data) == 3:
        name = f'{data[0]} {data[1]}'
        second_name = data[3]
    else:
        name, second_name = data
    students = Student.objects.filter(name=name, second_name=second_name)
    if len(students) == 0:
        return redirect('../../headmaster')
    
    teachers = Teacher.objects.filter(room=students[0].room)
    if len(teachers) == 0:
        teacher = None
    else:
        teacher = teachers[0]

    return render(response, "main/user_s.html", {"student":students[0], "teacher": teacher})

def user_t(response, full_name):
    if not response.session.get('auth') or not response.session.get('id'):
        return redirect('/../../login')

    t = Teacher.objects.filter(id=int(response.session.get('id')))[0]
    if not t.master:
        return redirect('/../../teacher')

    if response.method == "POST":
        if response.POST.get('logout'):
            response.session['auth'] = False
            response.session['id'] = None
            return redirect('/../../login')
        elif response.POST.get('master'):
            return redirect('/../../teacher')
        elif response.POST.get('panel'):
            return redirect('/../../headmaster')

    data = full_name.split(' ')
    if len(data) == 3:
        name = f'{data[0]} {data[1]}'
        second_name = data[2]
    else:
        name, second_name = data
    teachers = Teacher.objects.filter(name=name, second_name=second_name)
    if len(teachers) == 0:
        return redirect('../../headmaster')

    return render(response, "main/user_t.html", {"teacher": teachers[0]})