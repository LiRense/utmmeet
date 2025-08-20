from random import *
from string import *
from datetime import datetime as dt

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








