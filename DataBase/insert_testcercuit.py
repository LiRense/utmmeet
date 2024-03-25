from connection import *
from other.makr import gen_150_mark
from rstr import xeger

connection_db = Connecting()
tunnel = connection_db.tooneling(jump_host='10.0.50.208', jump_port=20010, remote_host='10.10.4.7', remote_port=57350, username='martikhin',
                                 ssh_pkey='/home/ivan/.ssh/id_rsa')

pov = 10000
col = 100
alk = '200'
serial = '200'
number = '00084000'
for j in range(pov):
    marks = []
    for i in range(col):
        mark = gen_150_mark(alk,serial,number)
        marks.append((f'{alk}', f'{serial}', f'{number}', f'{mark}', 0))
        # mark = (f'200200{number}0224001' + xeger(r'\w{100}') + xeger(r'\w{29}')).upper()
        # val = (alk,serial,number,mark,0)
        number = str(int(number) + 1)
        number = '0' * (8 - len(number)) + number
        print(i+1,' || appended || ', mark)
    print(marks)

    select_templates = ("INSERT INTO StampArchive.dbo.mark_list_FSM_MSK_FAB (type_mark, series, number, hash, ranges_processing_id) "
                        "VALUES(%s, %s, %s, %s, %d)")

