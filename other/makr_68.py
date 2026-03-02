from datetime import date
from random import randint, choices
import string

def gen_68_mark(product_code):
    today = date.today()

    n = int(product_code)
    b36 = ''
    while n:
        n, remainder = divmod(n, 36)
        b36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[remainder] + b36

    version = '22N'
    base36_code = b36 or '0'
    job_year = str(today.year)[-1:]
    job_month = f'{today.month:02d}'
    job_day = f'{today.day:02d}'
    jobcode = f'084U{job_year}{job_month}{job_day}001'
    num_mark = '000001'
    random_bit = str(randint(0, 1))
    random_number = str(randint(100, 999))
    random_chars = ''.join(choices(string.ascii_uppercase + string.digits, k=31))

    return f'{version}{base36_code}{jobcode}{num_mark}{random_bit}{random_number}{random_chars}'

for i in range(1,21):
    print(f"{i}) {gen_68_mark('0300003727440000047')}")