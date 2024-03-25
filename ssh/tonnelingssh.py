import pymssql
import sshtunnel, paramiko
import time

try:
    with sshtunnel.SSHTunnelForwarder(('10.0.50.208', 20010), ssh_username="martikhin",
                                      ssh_pkey=paramiko.RSAKey.from_private_key_file("/home/ivan/.ssh/id_rsa"),
                                      ssh_private_key_password="", remote_bind_address=('10.10.4.139', 1433)) as server:
        server.start()
        conn = pymssql.connect(
            host='127.0.0.1',
            port=server.local_bind_port,
            user='repp',
            password='LinkedServer123',
            database='EgaisNSI_test')
        curs = conn.cursor()
        start = time.time()
        curs.execute("SELECT c.* FROM Clients c with(nolock) inner join Clients_Status cs with(nolock) on cs.owner_id = c.owner_id WHERE cs.Status_Id = 'Active' and INN = '7743931676'")
        r = [dict((curs.description[i][0], value) for i, value in enumerate(row)) for row in curs.fetchall()]
        length = len(r)
        curs.close()
        conn.close()
        server.close()
        end = time.time()
        print(r)
        print("time = ",round(end-start,2),length)


except:
    print("Failed")


# server = Connecting.tooneling('10.0.50.208', 20010, '10.10.4.139', 1433, 'martikhin',
#                               "/home/ivan/.ssh/id_rsa", '')
# data.txt = Connecting.ms_sql(server,'EgaisNSI_test','repp','LinkedServer123')