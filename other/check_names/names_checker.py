from datetime import date
from pathlib import Path
import re

import datetime

mass = []
p = Path("/home/ivan/Загрузки/smev_archives/Smev_archive_2023")
for x in p.rglob("*"):
    x = re.sub('/home.*Smev_archive_2023/archive_', '',str(x))
    x = re.sub('_.*.zip', '', str(x))
    mass.append(x)
mass.sort()
start = ['2023','03','17']
start = list(map(int,start))
end = '2024-08-14'
print('status  |     start      |      end       |')
for i in mass:
    j = i.split('-')
    j = list(map(int, j))
    date_days = (datetime.date(j[0],j[1],j[2])-datetime.date(start[0],start[1],start[2])).days
    if date_days == 1:
        start = j
        # print('WOW',j, date_days)
    else:
        if len(str(start))>12:
            print(f'  NON   | {start}  | {j}  |')
        else:
            print(f'  NON   | {start}   | {j}   |')
        start=j

