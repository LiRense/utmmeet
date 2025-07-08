import json
import logging
import time
import xml.etree.ElementTree as ET
from datetime import date
import psycopg2
from kafka import KafkaProducer, KafkaConsumer
from psycopg2 import sql
from loguru import logger
import uuid


class Forming_xml():
    def __init__(self, doc_type='repproducedproduct_v4', fsrar='030000434308', product_code='0300004343080000007', quantity='1', alc_percent='40', ex_path='example/RepProducedProduct_v4.xml'):
        self.fsrar = fsrar
        self.product_code = product_code
        self.quantity = quantity
        self.alc_percent = alc_percent
        self.ex_path = ex_path
        self.doc_type = doc_type


    def get_day(self):
        logger.debug('Получаю дату документа')
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        return str(formatted_date)


    def generate_RPP(self):

        logger.debug('Генерирую xml')

        with open(self.ex_path, 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

            # FSRAR_ID
            root[0][0].text = self.fsrar
            # Date
            root[1][0][1][2].text = self.get_day()
            # ProducedDate
            root[1][0][1][3].text = self.get_day()
            # ClientRegId
            root[1][0][1][3].text = self.fsrar
            # ProductCode
            root[1][0][2][0][0].text = self.product_code
            # Quantity
            root[1][0][2][0][1].text = self.quantity
            # alcPercent
            root[1][0][2][0][2].text = self.alc_percent

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            return corrected_xml

class DB_placer():
    def __init__(self, db, user, password, host, port, sql_req=''):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.sql_req = sql_req

    def inserter(self):

        logger.debug('Выполняю insert')

        try:
            # Подключаемся к БД
            conn = psycopg2.connect(
                dbname = self.db,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )

            logger.debug('Подлючение к Postgre успешно')
            # Создаем курсор
            cursor = conn.cursor()

            query, params = self.sql_req

            logger.debug('Запрос выполняется')

            cursor.execute(query, params)
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Ошибка при работе с PostgreSQL: {error}")
        finally:
            # Закрываем соединение
            if hasattr(self, 'conn') and self.conn is not None:
                self.conn.close()
                logging.debug("Соединение с PostgreSQL закрыто")


    def text_to_hex(self,text_string):

        logger.debug('Конвертирую xml в hex')

        encoded_bytes = text_string.encode('utf-8')
        hex_representation = encoded_bytes.hex()

        return hex_representation

    def prepare_sql(self, file):
        logger.debug('Собираю sql запрос')
        current_ts = date.today().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        file_uuid = str(uuid.uuid4())

        return """
        INSERT INTO filedata.inboxdata
            (ts, uri, filedata, chunksize)
        VALUES
            (%s, %s, decode(%s, 'hex'), %s);
        """, (current_ts, file_uuid, file, 1000000)

class Kafka_sender():
    def __init__(self, doc_type, uuid, fsrar='030000434308', inn='7841051711'):
        self.doc_type = doc_type
        self.uuid = uuid
        self.fsrar = fsrar
        self.inn = inn
        self.date = self.get_day()
        self.timezone = '+03:00'
        self.kpp = ''

    def json_creator(self):
        raw_message = {
            "type": self.doc_type,
            "uri": str(self.fsrar + "-" + self.uuid),
            "fsrarid": self.fsrar,
            "date": self.date,
            "timezone": self.timezone,
            "inn": self.inn,
            "kpp": self.kpp
        }
        return raw_message

    def send(self):
        message = self.json_creator()

        bootstrap_server = ['test-kafka1.fsrar.ru:9092', 'test-kafka2.fsrar.ru:9092', 'test-kafka3.fsrar.ru:9092']
        topic = 'confirmed'

        producer = KafkaProducer(
            bootstrap_servers=bootstrap_server,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
        )
        producer.send(topic, message)
        logger.debug(f'Сообщение отправлено в топик {topic}')
        producer.close()


    def get_day(self):
            logger.debug('Получаю дату документа')
            today = date.today()
            formatted_date = today.strftime("%Y-%m-%d")
            return str(formatted_date)

class Result_checker():
    def __init__(self):
        pass


    def find_message_by_uri(self, uri: str, max_attempts=3, retry_interval=60):
        attempt = 0

        while attempt < max_attempts:
            consumer = KafkaConsumer(
                "svs-inspector",
                bootstrap_servers=['test-kafka1.fsrar.ru:9092', 'test-kafka2.fsrar.ru:9092', 'test-kafka3.fsrar.ru:9092'],
                auto_offset_reset='earliest',  # Читать с начала топика
                consumer_timeout_ms=10000,  # Таймаут ожидания новых сообщений (10 сек)
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )

            logger.debug(f"Попытка {attempt + 1} из {max_attempts}")

            try:
                for message in consumer:
                    msg_value = message.value
                    if msg_value.get('uri') == uri:
                        logger.debug("Сообщение найдено!")
                        return msg_value

                logger.debug(f"Сообщение с URI '{uri}' не найдено в текущей попытке")
            except Exception as e:
                logger.debug(f"Ошибка при чтении из Kafka: {e}")
            finally:
                consumer.close()

            attempt += 1
            if attempt < max_attempts:
                logger.debug(f"Повторная попытка через {retry_interval} секунд...")
                time.sleep(retry_interval)

        logger.debug(f"Сообщение с URI '{uri}' не найдено после {max_attempts} попыток")
        return None

if __name__ == "__main__":

    forming = Forming_xml()
    corr_xml = forming.generate_RPP()
    logger.debug('Успех генерации xml')

    db_ins = DB_placer('transport','dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
    hex_xml = db_ins.text_to_hex(corr_xml)
    query, params = db_ins.prepare_sql(hex_xml)
    db_ins.sql_req = (query, params) # Кортеж
    db_ins.inserter()
    logger.debug('Успех вставки в БД')

    sender = Kafka_sender(forming.doc_type, params[1])
    sender.send()
    logger.debug('Успех отправки json')

    result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))



