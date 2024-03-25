import re
from datetime import datetime

filename = 'check_status3.log'

with open(filename, 'r') as f:
    lines = f.readlines()
    lines = lines[:-1]

with open(filename, 'w') as f:
    f.writelines(lines)

def replacer(line):
    new_line = line.strip()
    print('1 ',new_line)
    new_line = new_line.replace(' INFO ','=')
    new_line = re.sub('GET.*- ', '=ZAZ ', new_line)
    new_line = re.sub('=.*=', '', new_line)
    new_line = new_line.replace(' ms', '')
    first = re.sub('2024.*ZAZ ', '', new_line)
    new_line = new_line[:-len(first)-5]
    print('2 ',new_line)
    print('3 ',first)
    datetime_object = datetime.strptime(new_line, '%Y-%m-%d %H:%M:%S.%f')
    return datetime_object,first

file2 = open('new.txt','w')
with open(filename, 'r') as file:
    line = file.readline()
    sup_date,first = replacer(line)
with open(filename, 'r') as file:
    for line in file:
        datetime_object,first = replacer(line)
        print(datetime_object)
        print(first)
        file2.writelines(f"[{round((datetime_object-sup_date).total_seconds(),2)},{int(first)/1000}]\n")
file2.close()
