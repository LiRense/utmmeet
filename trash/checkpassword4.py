import paramiko
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
pid = 12345 # Modify this per your requirement
try:
    ssh_client.connect('source',username='user',password='pwd')
    stdin,stdout,stderr = ssh_client.exec_command('sudo -k lsof -p '+pid)
    stdin.write('pwd\n')
    stdin.flush()
    result = stdout.read.splitlines()
except paramiko.SSHException:
    print('Connection Failed')
    quit()