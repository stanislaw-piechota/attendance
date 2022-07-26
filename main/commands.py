import qrcode as qr
import os
from random import choice

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

        