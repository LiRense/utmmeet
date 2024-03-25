import sshtunnel, psycopg2,paramiko
def bd():
    try:
        with sshtunnel.SSHTunnelForwarder(('10.0.50.208', 20010),ssh_username="martikhin",ssh_pkey=paramiko.RSAKey.from_private_key_file("/home/ivan/.ssh/id_rsa"),
                                              ssh_private_key_password="",remote_bind_address=('10.10.4.172', 5432)) as server:
            server.start()
            conn = psycopg2.connect(host= '127.0.0.1',
                                port=server.local_bind_port,
                                user='ci',
                                password='ci',
                                database='docs')
            print('connected')
            cursor = conn.cursor()
            # cursor.execute('SELECT *  FROM actwriteoff order by id desc limit 1')# Получаем список всех пользователей
            cursor.execute('SELECT *  FROM waybill order by id desc limit 1')
            AWO_transp = cursor.fetchall()
            cursor.close()  # закрываем курсор
            print(AWO_transp)

            conn.close()
            server.close()
            print("closed all")
            return AWO_transp
    except:
        print("Connection failed")

bd()