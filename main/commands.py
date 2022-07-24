import qrcode as qr
import bcrypt as b
import sys
import os

if len(sys.argv) <= 1:
    print('''generate:       generuj nowe kody qr
reset_teachers: resetuj pola class_name oraz room
check_pins:     sprawdź uniklaność pinów nauczycieli
check_names:    sprawdź poprawnośc loginów nauczycieli''')
    sys.exit(1)

if sys.argv[1] == 'generate':
    address = sys.argv[2]
    new = address.split('//')[1].split(':')[0]
    rooms = [27, 28, 29, 101, 102, 103, 104, 105, 106, 107, 201, 202, 203, 204, 205, 206, 207, 301, 303, 304, 306, 307]

    if not os.path.exists(f'../qr_codes/{new}'):
        os.mkdir(f"../qr_codes/{new}")
    for room in rooms:
        if not os.path.exists(f'../qr_codes/{new}/{room}'):
            os.mkdir(f'../qr_codes/{new}/{room}')
        for row in range(1, 6):
            for col in range(1, 7):
                st = f'{address}/student/?room={room}&row={row}&col={col}&checksum='
                if row and col:
                    check = room*row//col
                else:
                    check = room+2137
                st += b.hashpw(str(check).encode(), b.gensalt()).decode()
                img = qr.make(st)
                print(f'{room},{row},{col}')
                img.save(f'../qr_codes/{new}/{room}/{row},{col}.png')

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
    for i in range(7):
        row = input()
        for j, sign in enumerate(row):
            if sign == ' ':
                empty = True
            else:
                empty = False

            model.objects.create(room=room, row=i+1, col=j+1, empty=empty)
            
