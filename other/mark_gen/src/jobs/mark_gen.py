import sys
import os
import psycopg2
from datetime import datetime
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from z11_gen import Generator


class GeneratorBcode:
    def __init__(self, type_mark='200', series='200', db_host=None, db_port=None, db_name=None, db_user=None,
                 db_password=None):
        self.type_mark = type_mark
        self.series = series
        self.db_host = db_host or os.getenv('DB_HOST')
        self.db_port = db_port or os.getenv('DB_PORT', '5432')
        self.db_name = db_name or os.getenv('DB_NAME')
        self.db_user = db_user or os.getenv('DB_USER')
        self.db_password = db_password or os.getenv('DB_PASSWORD')

    @staticmethod
    def gen(alk: str, serial: str, number: str):
        if len(number) <= 8:
            month = str(datetime.now().month)
            month = '0' * (2 - len(month)) + month
            year = str(datetime.now().year)[-2:]
            version = '001'
            kript = ''

            a = Generator()
            kript = Generator.gen_vers(a, n=129)
            return alk + serial + str(number) + month + year + version + kript
        else:
            raise ValueError('Length of number must be 8 or less')

    def get_last_number(self):
        query = """
            SELECT x."number" FROM public.mark_list AS x
            WHERE type_mark = %s
            AND series = %s
            ORDER BY id DESC 
            LIMIT 1
        """

        try:
            result = self.get_single_int_from_db(query, (self.type_mark, self.series))
            logger.info(f"Последний номер в БД: {result}")
            return result
        except ValueError:
            logger.info("Нет записей в БД, начинаем с 0")
            return 0
        except Exception as e:
            logger.error(f"Ошибка при получении последнего номера: {e}")
            raise

    def generate_records(self, base_number: int, count: int = 10):
        for i in range(count):
            current_number = base_number + i + 1
            number_str = str(current_number).zfill(8)

            hash_value = self.gen(self.type_mark, self.series, number_str)

            yield (
                self.type_mark,  # type_mark
                self.series,  # series
                number_str,  # number (строка)
                datetime.now(),  # date_insert
                hash_value,  # hash
                current_number  # num (число)
            )

    def get_db_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            logger.debug("Успешное подключение к БД")
            return conn
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    def get_single_int_from_db(self, query, params=None):
        conn = None
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()

                if result is None:
                    raise ValueError("Запрос не вернул результатов")

                return int(result[0])

        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Соединение с БД закрыто")

    def insert_multiple_records(self, query, records):
        conn = None
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cursor:
                cursor.executemany(query, records)
                conn.commit()
                logger.success(f"Успешно вставлено {len(records)} записей")

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Ошибка при вставке данных: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def insert_mark_list_records(self, count: int = 10):
        try:
            logger.info(f"Начало вставки {count} записей")

            last_number = self.get_last_number()
            logger.info(f"Последний номер в БД: {last_number}")

            records = list(self.generate_records(last_number, count))
            logger.info(f"Сгенерировано {len(records)} записей")

            query = """
                INSERT INTO public.mark_list 
                    (type_mark, series, "number", date_insert, hash, num)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            self.insert_multiple_records(query, records)

            logger.success(f"Вставлено {len(records)} записей. Последний номер: {records[-1][5]}")

        except Exception as e:
            logger.error(f"Ошибка в insert_mark_list_records: {e}")
            raise