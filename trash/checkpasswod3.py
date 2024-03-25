#import the pexpect module
import pexpect
# here you issue the command with "sudo"
child = pexpect.spawn('sudo /usr/sbin/lsof')
# it will prompt something like: "[sudo] password for < generic_user >:"
# you "expect" to receive a string containing keyword "password"
child.expect('password')
# if it's found, send the password
child.sendline('S3crEt.P4Ss')
# read the output
print(child.read())
# the end