import datetime
import random
from random import sample
from string import ascii_letters, digits


def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
    base36 = ''
    sign = ''
    if number < 0:
        sign = '-'
        number = -number
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign + base36

def base36decode(number):
    return int(number, 36)

def month(num):
    if num < 10:
        return '0'+str(num)
    else:
        return str(num)

def gen_vers(n):
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

today = datetime.date.today()

version = '22N'
alcode_base_10 = 300004343080000001
alcode_base_36 = base36encode(alcode_base_10)
jobcode = '084U'+str(today.year)[-1:]+month(today.month)+month(today.day)+'001'
num_mark = '000001' #номер марки в заявке

for i in range(6):
    print('<ce:amc>'+version+alcode_base_36+jobcode+num_mark+str(random.randint(0,1))+str(random.randint(100,999))+gen_vers(31)+'</ce:amc>')
