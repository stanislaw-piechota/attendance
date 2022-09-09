import encodings
import qrcode as qr
import os
from random import choice
from datetime import datetime as dt
import json
from shutil import rmtree

def draw_room(model, room):
    seats = model.objects.filter(room=room)

    plan = [['' for _ in range(8)] for _ in range(8)]
    st = ''

    for seat in seats:
        if seat.empty:
            mark = ' '
        else:
            mark = '-'

        plan[seat.row-1][seat.col-1] = mark

    for row in plan:
        st = f"{''.join(row)}\n{st}"

    print(st)

def create_room(model, room):
    for i in range(8):
        row = input()
        for j, sign in enumerate(row):
            if sign == ' ':
                empty = True
            else:
                empty = False

            model.objects.create(room=room, row=i+1, col=j+1, empty=empty)
            
def create_qr(model, room):
    seats = model.objects.filter(room=room)
    if not os.path.exists(str(room)):
        os.mkdir(str(room))
    for seat in seats:
        if not seat.empty:
            print(seat.room, seat.row, seat.col)
            checksum = encrypt(f'{seat.room}/{seat.row}/{seat.col}')
            print(checksum, decrypt(checksum))
            code = f'https://plopl-attendance.herokuapp.com/student/?room={room}&row={seat.row}&col={seat.col}&checksum={checksum}'
            img = qr.make(code)
            img.save(f'{room}/{seat.row},{seat.col}.png')

def QRs():
    from .models import Seat as model

    try:
        os.chdir('qr_codes/plopl-attendance.herokuapp.com')
    except:
        pass

    rooms = [27,28,29,101,102,103,104,105,106,107,201,202,203,204,205,206,207,301,303,305,306,307]
    for room in rooms:
        create_qr(model, room)

def create_seats(model):
    with open('seats.txt') as file:
        data = file.read().split('\n')
    
    ind = 0
    room = 0
    row = 0
    while ind < len(data):
        line = data[ind]
        if ('.' not in line) and (' ' not in line):
            room = int(line)
            row = 0
            print(f'--{room}--')
        else:
            row += 1
            for col, sign in enumerate(line):
                print(f'{row}, {col}')
                model.objects.create(room=room, row=row, col=col+1, empty=sign==' ')
        ind += 1

def encrypt(string: str):
    codes = [ord(l) for l in string]
    result = ''
    add = [0, 24, 57]
    
    for i, code in enumerate(codes):
        if code+i>59:
            code -= i
        else:
            code += i

        code += choice(add)

        result += chr(code)
    return result

def decrypt(string: str):
    codes = [ord(l) for l in string]
    result = ''

    for i, code in enumerate(codes):
        if 64<=code<=90:
            code -= 24
        elif 97<=code<=122:
            code -= 57

        if code-i<47:
            code += i
        else:
            code -= i

        result += chr(code)
    return result

def create_report(present, absent, class_name, room, teacher):
    date = dt.now()
    if date.hour < 8 or date.hour > 15:
        return
    if not os.path.exists('main/reports'):
        os.mkdir('main/reports')
    filepath = f"main/reports/{date.strftime('%d-%m-%Y')}"
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    payload = {}
    payload['lesson'] = date.hour-7
    payload['teacher'] = f"{teacher.name} {teacher.second_name}"
    payload['created'] = date.strftime("%H:%M:%S, %d.%m.%Y")
    payload['class'] = class_name
    payload['classroom'] = room
    payload['present'], payload['absent'] = [], []
    for person in present:
        payload['present'].append({
            "name": person.name,
            "second name": person.second_name,
            "activity": person.last_time.strftime("%H:%M:%S, %d.%m.%Y")
        })
    for person in absent:
        payload['absent'].append({
            "name": person.name,
            "second name": person.second_name
        })
    filepath += f"/{class_name}"
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    filepath += f"/lesson-{payload['lesson']}.json"
    with open(filepath, "wb") as file:
        file.write(json.dumps(payload, indent=2, ensure_ascii=False).encode('utf-8'))
        
def delete_raports():
    date = dt.now()
    for folder in os.listdir('main/reports')[::]:
        f_date = dt.strptime(folder, '%d-%m-%Y')
        if (date-f_date).days > 30:
            rmtree(f'./main/reports/{folder}')
