import re

with open('new_lena.txt', 'r') as fiiles:
    lots_lines = fiiles.readlines()
new_lines = []
flag = 0
for i in lots_lines:
    if '<pre>' in i:
        new_lines.append(i)
        flag = 1
        continue
    elif '</pre>' in i:
        flag = 0
    if flag==0:
        i = re.sub("!.*.png!","",i)
        new_lines.append(i)

with open('without_pre.txt', 'w') as fp:
    for item in new_lines:
        fp.write("%s" % item)
    print('Done')
