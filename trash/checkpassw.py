import getpass
import subprocess

sudo_password = getpass.getpass(prompt='sudo password: ')
p = subprocess.Popen(['sudo', '-S', 'ls'], stderr=subprocess.PIPE, stdout=subprocess.PIPE,  stdin=subprocess.PIPE)

try:
    out, err = p.communicate(input=(sudo_password+'\n').encode(),timeout=5)
    print('ok')

except subprocess.TimeoutExpired:
    p.kill()
    print('bad')