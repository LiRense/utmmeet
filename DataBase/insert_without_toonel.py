import pymssql
from datetime import datetime as dt
from random import *
from string import *

class Generator():
    def substring(self,string,start,lenght):
        return string[start:start+lenght]

    def gen_number_code(self,lenght):
        start = 10 ** (lenght - 1)
        end = (10 ** lenght) - 1
        return str(randint(start, end))

    def gen_vers(self,n):
        i=1
        letters_and_digits = ascii_letters + digits
        endword = ""
        if n > 36:
            i = n//36
            if n//36 != 0:
                i+=1
                for j in range(i-1):
                    rand_string = ''.join(sample(letters_and_digits, 36))
                    endword+=rand_string
                rand_string = ''.join(sample(letters_and_digits, n%36))
                endword += rand_string
            elif n//36 == 0:
                for j in range(i):
                    rand_string = ''.join(sample(letters_and_digits, 36))
                    endword += rand_string
        else:
            rand_string = ''.join(sample(letters_and_digits, n))
            endword += rand_string

        return str(endword.upper())

    def convert(self,word,base):
        res = ""
        alph = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if base > len(alph):None
        while word>0:
            res = alph[word%base]+res
            word//=base
        return res.upper()

    def gen_allcode(self):
        allcode_10 = randint(0,99999999999999999)
        allcode_36 = self.convert(allcode_10,36)
        if len(allcode_36) < 16:
            zero_add = "0"*(16 - len(allcode_36))
            allcode_36 = zero_add + allcode_36
        return allcode_36

    def gen_djob_code(self):
        nabor = '0123ABCD'
        val = ''
        for i in range(4):
            val += choice(nabor)
        dat = str(dt.now())
        god = dat[3]
        mes = dat[5:7]
        day = dat[8:10]
        work_num = str(randint(0,999))
        if len(work_num) < 3:
            work_num = "0"* (3-len(work_num)) +  work_num
        code = str(val) + str(god) + str(mes) + str(day) + work_num
        return code
def gen_150_mark(alk: str, serial: str, number: str):
    if len(number) <= 8:
        # alk = "200"
        # serial = '200'
        # number = '00000000'  # uniq 8 len
        month = str(dt.now().month)
        month = '0'*(2-len(month))+month
        year = str(dt.now().year)[-2:]
        version = '001'
        kript = ''

        a = Generator()
        kript = Generator.gen_vers(a,n=129)
        # print('<gz:NCode>'+alk+serial+str(number)+month+year+version+kript+'</gz:NCode>')
        # number = str(int(number)+1)
        # number = '0'*(8-len(number))+number
        # print(datetime.now())
        return alk+serial+str(number)+month+year+version+kript
    else:
        print('Lenght of number must be 8 or less')

def without_toonel_ms_sql(host_db: str, port: int, db_name: str, db_user: str, db_password: str = None,
                          request: str = 'SELECT @@SERVERNAME', values: list = None):
    try:
        conn = pymssql.connect(host=host_db,
                               port=port,
                               user=db_user,
                               password=db_password,
                               database=db_name)
        curs = conn.cursor()
        curs.executemany(request, values)
        print(curs.rowcount, "record inserted.")
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print(e, "Fail, check settings for user, password or database")

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

    without_toonel_ms_sql('10.0.50.208',20010,'StampArchive','invoiceissueam','jDn(4SkE', select_templates, marks)