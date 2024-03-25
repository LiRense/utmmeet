import zz.z11
from datetime import datetime as dt


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

        a = zz.z11.Generator()
        kript = zz.z11.Generator.gen_vers(a,n=129)
        # print('<gz:NCode>'+alk+serial+str(number)+month+year+version+kript+'</gz:NCode>')
        # number = str(int(number)+1)
        # number = '0'*(8-len(number))+number
        # print(datetime.now())
        return alk+serial+str(number)+month+year+version+kript
    else:
        print('Lenght of number must be 8 or less')

print(gen_150_mark('200','200','00456001'))
print(gen_150_mark('200','200','00456002'))
print(gen_150_mark('200','200','00456003'))
print(gen_150_mark('200','200','00456004'))
