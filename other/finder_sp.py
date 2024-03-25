import subprocess
import sys
def find_sp():
    ls = subprocess.Popen(["ls", "/opt/utm/transport/lib", "-p"],
                          stdout=subprocess.PIPE)
    grep = subprocess.Popen(["grep", " sp-1."],
                        stdin=ls.stdout,
                        stdout=subprocess.PIPE)
    endOfPipe = grep.stdout
    for i in endOfPipe:
        print(i)


find_sp()