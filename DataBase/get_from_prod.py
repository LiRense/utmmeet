from connection import *

connection_db = Connecting()
tunnel = connection_db.tooneling(jump_host='10.0.50.208', jump_port=20010, remote_host='10.10.4.172', remote_port=5432, username='martikhin',
                                 ssh_pkey='/home/ivan/.ssh/id_rsa')

print(connection_db.pg_sql(tunnel,'svs','ci','ci',"select 1"))

