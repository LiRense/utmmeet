import os, subprocess
from getpass import getpass

def is_root():
    return os.geteuid() == 0

def o_test_sudo(pwd=""):
    args = "sudo -S echo OK".split()
    kwargs = dict(stdout=subprocess.PIPE,
                  encoding="ascii")
    if pwd:
        kwargs.update(input=pwd)
    cmd = subprocess.run(args, **kwargs)
    return ("OK" in cmd.stdout)

def prompt_sudo():
    ok = is_root() or o_test_sudo()
    if not ok:
        pwd = 'gelp'
        ok  = o_test_sudo(pwd)
    return ok

while True:
    if prompt_sudo():
        print("Access granted !")
        break
    else:
        print("Access denied !")
        break