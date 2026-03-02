import paramiko
import psycopg2
import pymssql
import sshtunnel
from typing import Optional, Union, List, Tuple, Any


class DBConnector:
    """Универсальный коннектор к БД через SSH tunnel"""

    def __init__(self,
                 jump_host: str,
                 jump_port: int,
                 remote_host: str,
                 remote_port: int,
                 username: str,
                 ssh_pkey: str,
                 ssh_private_key_password: Optional[str] = None):
        """
        Инициализация подключения

        Args:
            jump_host: Хост для SSH прыжка
            jump_port: Порт для SSH прыжка
            remote_host: Целевой хост БД
            remote_port: Порт целевой БД
            username: Имя пользователя SSH
            ssh_pkey: Путь к приватному ключу SSH
            ssh_private_key_password: Пароль для ключа (опционально)
        """
        self.jump_host = jump_host
        self.jump_port = jump_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.username = username
        self.ssh_pkey = ssh_pkey
        self.ssh_private_key_password = ssh_private_key_password
        self.server = None
        self.connection = None

    def create_ssh_tunnel(self) -> sshtunnel.SSHTunnelForwarder:
        """Создание SSH тунеля"""
        try:
            self.server = sshtunnel.SSHTunnelForwarder(
                (self.jump_host, self.jump_port),
                ssh_username=self.username,
                ssh_pkey=paramiko.RSAKey.from_private_key_file(
                    self.ssh_pkey,
                    password=self.ssh_private_key_password
                ),
                remote_bind_address=(self.remote_host, self.remote_port)
            )
            return self.server
        except Exception as e:
            raise Exception(f"SSH tunnel creation failed: {e}")

    def connect_postgresql(self,
                           db_name: str,
                           db_user: str,
                           db_password: str,
                           **kwargs) -> psycopg2.extensions.connection:
        """Подключение к PostgreSQL"""
        if not self.server:
            self.create_ssh_tunnel()
            self.server.start()

        try:
            self.connection = psycopg2.connect(
                host='127.0.0.1',
                port=self.server.local_bind_port,
                user=db_user,
                password=db_password,
                database=db_name,
                **kwargs
            )
            return self.connection
        except Exception as e:
            raise Exception(f"PostgreSQL connection failed: {e}")

    def connect_sqlserver(self,
                          db_name: str,
                          db_user: str,
                          db_password: str,
                          **kwargs) -> pymssql.Connection:
        """Подключение к SQL Server"""
        if not self.server:
            self.create_ssh_tunnel()
            self.server.start()

        try:
            self.connection = pymssql.connect(
                server='127.0.0.1',
                port=self.server.local_bind_port,
                user=db_user,
                password=db_password,
                database=db_name,
                **kwargs
            )
            return self.connection
        except Exception as e:
            raise Exception(f"SQL Server connection failed: {e}")

    def execute_query(self,
                      query: str,
                      params: Optional[Tuple] = None,
                      fetch: bool = True) -> Union[List[Tuple], int, None]:
        """
        Выполнение SQL запроса

        Args:
            query: SQL запрос
            params: Параметры для запроса (для предотвращения SQL injection)
            fetch: Нужно ли возвращать результат

        Returns:
            Результат запроса или количество affected rows
        """
        if not self.connection:
            raise Exception("No active connection. Call connect_* method first.")

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)

                if fetch and query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return cursor.rowcount

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Query execution failed: {e}")

    def execute_many(self,
                     query: str,
                     params_list: List[Tuple]) -> int:
        """
        Массовое выполнение запроса

        Args:
            query: SQL запрос
            params_list: Список параметров

        Returns:
            Общее количество affected rows
        """
        if not self.connection:
            raise Exception("No active connection. Call connect_* method first.")

        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(query, params_list)
                self.connection.commit()
                return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Bulk execution failed: {e}")

    def close(self):
        """Закрытие соединений"""
        if self.connection:
            self.connection.close()
            self.connection = None

        if self.server:
            self.server.stop()
            self.server = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Класс для быстрого доступа (старый интерфейс)
class Connecting:
    """Упрощенный интерфейс для обратной совместимости"""

    @staticmethod
    def tooneling(jump_host: str, jump_port: int, remote_host: str, remote_port: int,
                  username: str, ssh_pkey: str, ssh_private_key_password: str = None):
        return DBConnector(jump_host, jump_port, remote_host, remote_port,
                           username, ssh_pkey, ssh_private_key_password)

    @staticmethod
    def pg_sql(server_data: DBConnector, db_name: str, db_user: str,
               db_password: str = None, request: str = 'SELECT 1'):
        server_data.connect_postgresql(db_name, db_user, db_password)
        return server_data.execute_query(request)