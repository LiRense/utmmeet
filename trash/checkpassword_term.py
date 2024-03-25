import re
i = 'password: 1234\n'
if 'password: ' in i:
    password = re.sub('password: ','',i)
    print(password)