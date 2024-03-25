import paramiko
import psycopg2
import pymssql
import sshtunnel


class Connecting():
    @staticmethod
    def tooneling(jump_host: str, jump_port: int, remote_host: str, remote_port: int, username: str, ssh_pkey: str,
                  ssh_private_key_password: str = None):
        try:
            server = sshtunnel.SSHTunnelForwarder((jump_host, jump_port), ssh_username=username,
                                                  ssh_pkey=paramiko.RSAKey.from_private_key_file(ssh_pkey),
                                                  ssh_private_key_password=ssh_private_key_password,
                                                  remote_bind_address=(remote_host, remote_port))
            return server
        except Exception as e:
            print(e, "Fail, check settings for jump, ssh, remote")

    @staticmethod
    def ms_sql(server_data: sshtunnel.SSHTunnelForwarder, db_name: str, db_user: str, db_password: str = None,
               request: str = 'SELECT @@SERVERNAME'):
        with server_data as server:
            server.start()
            try:
                conn = pymssql.connect(host='127.0.0.1',
                                       port=server.local_bind_port,
                                       user=db_user,
                                       password=db_password,
                                       database=db_name)
                curs = conn.cursor()
                curs.execute(request)
                text = curs.fetchall()
                curs.close()
                conn.close()
                server.close()
                return text
            except Exception as e:
                print(e, "Fail, check settings for user, password or database")

    @staticmethod
    def insert_ms_sql(server_data: sshtunnel.SSHTunnelForwarder, db_name: str, db_user: str, db_password: str = None,
               request: str = 'SELECT @@SERVERNAME', value:tuple = None):
        with server_data as server:
            server.start()
            try:
                conn = pymssql.connect(host='127.0.0.1',
                                       port=server.local_bind_port,
                                       user=db_user,
                                       password=db_password,
                                       database=db_name)
                curs = conn.cursor()
                curs.execute(request, value)
                print(curs.rowcount, "record inserted.")
                conn.commit()
                curs.close()
                conn.close()
                server.close()
            except Exception as e:
                print(e, "Fail, check settings for user, password or database")

    @staticmethod
    def insert_multi_ms_sql(server_data: sshtunnel.SSHTunnelForwarder, db_name: str, db_user: str, db_password: str = None,
               request: str = 'SELECT @@SERVERNAME', values:list = None):
        with server_data as server:
            server.start()
            try:
                conn = pymssql.connect(host='127.0.0.1',
                                       port=server.local_bind_port,
                                       user=db_user,
                                       password=db_password,
                                       database=db_name)
                curs = conn.cursor()
                curs.executemany(request, values)
                print(curs.rowcount, "record inserted.")
                conn.commit()
                curs.close()
                conn.close()
                server.close()
            except Exception as e:
                print(e, "Fail, check settings for user, password or database")

    @staticmethod
    def pg_sql(server_data: sshtunnel.SSHTunnelForwarder, db_name: str, db_user: str, db_password: str = None,
               request: str = 'SELECT @@SERVERNAME'):
        with server_data as server:
            server.start()
            try:
                conn = psycopg2.connect(host='127.0.0.1',
                                        port=server.local_bind_port,
                                        user=db_user,
                                        password=db_password,
                                        database=db_name)
                curs = conn.cursor()
                curs.execute(request)
                text = curs.fetchall()
                curs.close()
                conn.close()
                server.close()
                return text
            except Exception as e:
                print(e, "Fail, check settings for user, password or database")

    @staticmethod
    def without_toonel_ms_sql(host_db:str, port:int, db_name: str, db_user: str, db_password: str = None, request: str = 'SELECT @@SERVERNAME', values:list = None):
        try:
            conn = pymssql.connect(host=host_db,
                                   port=port,
                                   user=db_user,
                                   password=db_password,
                                   database=db_name)
            curs = conn.cursor()
            curs.executemany(request, values)
            print(curs.rowcount, "record inserted.")
            conn.commit()
            curs.close()
            conn.close()
            return text
        except Exception as e:
            print(e, "Fail, check settings for user, password or database")