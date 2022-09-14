from base64 import encode
import qrcode as qr
import os
from random import choice
from datetime import datetime as dt
import json
from shutil import rmtree
from unidecode import unidecode
from secured_files.password import *
import smtplib, ssl
from email.message import EmailMessage

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

def send_mails(st, codes):
    with open('secured_files/to_send.txt', encoding='utf-8') as file:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(address, port, context=context) as server:
            server.login(mail, password)
            for line in file.readlines():
                data = line.split(',')
                if line == '':
                    continue
                if len(data[3]) > 1:
                    data[3] = data[3][0]
                receive_mail = f'u{data[2]}{data[3].lower()}{unidecode(data[1][0:3]).capitalize()}\
{unidecode(data[0][:3]).capitalize()}@liceum.p.lodz.pl'
                name, second_name, class_name = data[1], data[0], f"{22+1-int(data[2])}{data[3].upper()}"
                print(receive_mail, name, second_name, class_name)
                id = st.objects.filter(name=name, second_name=second_name, class_name=class_name)[0].id
                code = codes.objects.get(user_id=str(id))
                message = EmailMessage()
                message['From'] = mail
                message['To'] = receive_mail
                subject = "System obecności PLOPŁ"
                text = f"""
Kod weryfikacyjny dla ucznia: {name} {second_name}\n
{code}

Wygenerowane automatycznie, {dt.now().strftime('%H:%M:%S %d.%m.%Y')}.\n
Nie odpowiadaj na tą wiadomość.
"""
                message['Subject'] = subject
                message.set_content(text)
                server.sendmail(mail, receive_mail, message.as_string())
                with open('secured_files/students.txt', 'a', encoding='utf-8') as file2:
                    file2.write(f'{line}\n')
    with open('secured_files/to_send.txt', 'w') as file:
        print('done')

def create_db_users(st):
    with open('secured_files/to_send.txt', encoding='utf-8') as file:
        for line in file.readlines():
            data = line.split(',')
            st.objects.create(name=data[1], second_name=data[0], class_name=f"{23-int(data[2])}{data[3].capitalize()}")
