import json
import logging
import time
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from datetime import date
import psycopg2
from kafka import KafkaProducer, KafkaConsumer
from psycopg2 import sql
from loguru import logger
import uuid
from random import randint

from sqlalchemy import false

import BCode_gen


class Forming_xml():
    def __init__(self,
                 doc_type='repproducedproduct_v4',
                 fsrar='030000434308',
                 inn='7841051711',
                 kpp='770101008',
                 pr_name='Водка СИБИРСКИЙ ВОЛК',
                 product_code='0300004343080000007',
                 capacity='1',
                 alc_percent='40',
                 product_vcode='200',
                 quantity='1',
                 ip_inn='771391935319',
                 ip_fsrar='030043434308',
                 ip_name='ИП Мартихин Иван Андреевич',
                 ip_product_code ='0300434343080000007',
                 isUnPacked=False,
                 docId='PRODAP-0000000000',
                 isMark=True,
                 bcode="",
                 formA="FA-000000000000654",
                 formB="FB-000000000000006",
                 name='АКЦИОНЕРНОЕ ОБЩЕСТВО "ЦЕНТРИНФОРМ"',
                 isIp=False,
                 fixNum = ''):
        self.doc_type = doc_type.lower()
        self.docId = docId

        self.fsrar = fsrar
        self.inn = inn
        self.kpp = kpp

        self.pr_name = pr_name
        self.product_code = product_code
        self.capacity = capacity
        self.product_vcode = product_vcode
        self.alc_percent = alc_percent

        self.quantity = quantity

        self.ip_inn = ip_inn
        self.ip_fsrar = ip_fsrar
        self.ip_name = ip_name
        self.ip_product_code = ip_product_code

        self.isUnPacked = isUnPacked
        self.isMark = isMark

        self.bcode = bcode
        self.formA = formA
        self.formB = formB
        self.fixNum = fixNum

        self.name = name
        self.isIp = isIp



    def plus_docId(self):
        prefix, number_str = self.docId.split('-')
        number = int(number_str)
        new_number = number + 1
        new_number_str = f"{new_number:0{len(number_str)}d}"
        self.docId = f"{prefix}-{new_number_str}"

    def update_docId(self, new_number):
        prefix, number_str = self.docId.split('-')
        number = int(number_str)
        new_number_str = f"{new_number:0{len(number_str)}d}"
        self.docId = f"{prefix}-{new_number_str}"

    def gen_150_mark(self):
        number = str(randint(0,99999999))
        number = '0'*(8-len(number))+number

        alk = self.product_vcode
        serial = '200'

        month = str(datetime.now().month)
        month = '0' * (2 - len(month)) + month
        year = str(datetime.now().year)[-2:]

        version = '001'

        a = BCode_gen.Generator()
        kript = BCode_gen.Generator.gen_vers(a, n=129)

        return alk + serial + str(number) + month + year + version + kript

    def get_day(self):
        logger.debug('Получаю дату документа')
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        return str(formatted_date)

    def generate_RPP_4(self):

        self.docId = 'PRODAP-0000000090'

        logger.debug('Генерирую xml')

        with open(f'example/{self.doc_type}.xml', 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

            if self.doc_type == 'repproducedproduct_v4_ip':
                self.isIp = True
                self.doc_type = 'repproducedproduct_v4'
            elif self.doc_type == 'repproducedproduct_v4':
                self.isIp = False
                self.doc_type = 'repproducedproduct_v4'

            if self.isIp == False:

                # Num
                root[1][0][0].text = str(randint(0, 9999))
                root[1][0][1][1].text = str(randint(0, 9999))

                # FSRAR_ID
                root[0][0].text = self.fsrar
                # Date
                root[1][0][1][2].text = self.get_day()
                # ProducedDate
                root[1][0][1][3].text = self.get_day()
                # ClientRegId
                root[1][0][1][4][0][0].text = self.fsrar
                # Name
                root[1][0][1][4][0][1].text = self.name
                root[1][0][1][4][0][2].text = self.name
                # INN
                root[1][0][1][4][0][3].text = self.inn
                # KPP
                root[1][0][1][4][0][4].text = self.kpp
                # ProductCode
                root[1][0][2][0][0].text = self.product_code
                # Quantity
                root[1][0][2][0][1].text = self.quantity
                # alcPercent
                root[1][0][2][0][2].text = self.alc_percent
                # BCode
                root[1][0][2][0][5][0].text = self.gen_150_mark()
            elif self.isIp == True:
                # Num
                root[1][0][0].text = str(randint(0, 9999))
                root[1][0][1][1].text = str(randint(0, 9999))

                # FSRAR_ID
                root[0][0].text = self.ip_fsrar
                # Date
                root[1][0][1][2].text = self.get_day()
                # ProducedDate
                root[1][0][1][3].text = self.get_day()
                # ClientRegId
                root[1][0][1][4][0][0].text = self.ip_fsrar
                # Name
                root[1][0][1][4][0][1].text = self.ip_name
                root[1][0][1][4][0][2].text = self.ip_name
                # INN
                root[1][0][1][4][0][3].text = self.ip_inn
                # ProductCode
                root[1][0][2][0][0].text = self.ip_product_code
                # Quantity
                root[1][0][2][0][1].text = self.quantity
                # alcPercent
                root[1][0][2][0][2].text = self.alc_percent
                # BCode
                root[1][0][2][0][5][0].text = self.gen_150_mark()

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0]
                if len(position) > 5:
                    position.remove(position[5])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            return corrected_xml

    def generate_RIP_4(self):
        logger.debug('Генерирую xml')

        self.docId = 'IMP-0000000118'

        with open(f'example/{self.doc_type}.xml', 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

            # Num
            root[1][0][0].text = str(randint(0, 9999))
            root[1][0][1][0].text = str(randint(0, 9999))

            # FSRAR_ID
            root[0][0].text = self.fsrar
            # Date
            root[1][0][1][1].text = self.get_day()
            # ProducedDate
            root[1][0][1][2].text = self.get_day()

            # ClientRegId
            root[1][0][1][3][0][0].text = self.fsrar
            # INN
            root[1][0][1][3][0][3].text = self.inn
            # KPP
            root[1][0][1][3][0][4].text = self.kpp

            # ProductCode
            root[1][0][2][0][0].text = self.product_code
            # Quantity
            root[1][0][2][0][1].text = self.quantity
            # BCode
            root[1][0][2][0][8][0].text = self.gen_150_mark()

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0]
                if len(position) > 8:
                    position.remove(position[8])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            return corrected_xml

    def generate_ACO_2(self):
        logger.debug('Генерирую xml')

        self.docId = 'INV-0000000073'

        with open(f'example/{self.doc_type}.xml', 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

            # Num
            root[1][0][0].text = str(randint(0, 9999))
            root[1][0][1][0].text = str(randint(0, 9999))

            # FSRAR_ID
            root[0][0].text = self.fsrar
            # # Date
            root[1][0][1][1].text = self.get_day()

            # FullName
            root[1][0][2][0][1][2].text = self.pr_name
            # ProductCode
            root[1][0][2][0][1][3].text = self.product_code
            # capacity
            root[1][0][2][0][1][4].text = self.capacity
            # AlcVolume
            root[1][0][2][0][1][5].text = self.alc_percent
            # ProductVCode
            root[1][0][2][0][1][6].text = self.product_vcode
            # Quantity
            root[1][0][2][0][2].text = self.quantity
            root[1][0][2][0][3][0][0][0].text = self.quantity
            # BCode
            root[1][0][2][0][4][0].text = self.gen_150_mark()

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0]
                if len(position) > 4:
                    position.remove(position[4])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            return corrected_xml

    def generate_AWO_3(self):
        logger.debug('Генерирую xml')

        self.docId = 'AWO-0000000184'

        with open(f'example/{self.doc_type}.xml', 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

            # Num
            root[1][0][0].text = str(randint(0, 9999))
            root[1][0][1][0].text = str(randint(0, 9999))

            # FSRAR_ID
            root[0][0].text = self.fsrar
            # Date
            root[1][0][1][1].text = self.get_day()
            # Quantity
            root[1][0][2][0][1].text = self.quantity
            # formB
            root[1][0][2][0][2][0][0].text = self.formB
            # BCode
            root[1][0][2][0][3][0].text = self.bcode

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0]
                if len(position) > 3:
                    position.remove(position[3])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            return corrected_xml

    # Тут сложные тесты, сначала нужно поставить продукцию другой орге, потом через оргу отправить ТТН, потом с нас отправить AFBC на другую марку орги
    # Т. е. RPP_v4 2 марки На ИП
    # ТТН 1 марка с ИП на 030000434308
    # AFBC форма из ТТН, марка другая от ИП
    def generate_AFBC(self):
        logger.debug('Генерирую xml')

        self.docId = 'AFBC-0000000111'

        with open(f'example/{self.doc_type}.xml', 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

            logger.debug(root)
            # Num
            root[1][0][0].text = str(randint(0, 9999))
            root[1][0][1][0].text = str(randint(0, 9999))

            # FSRAR_ID
            root[0][0].text = self.fsrar
            # Date
            root[1][0][1][1].text = self.get_day()
            # formBа
            root[1][0][2][0][1].text = self.formB
            # BCode
            root[1][0][2][0][2][0].text = self.bcode

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0]
                if len(position) > 2:
                    position.remove(position[2])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            return corrected_xml

    def generate_TTN(self):
        logger.debug('Генерирую xml')

        self.docId = 'TTN-0000000213'

        with open(f'example/{self.doc_type}.xml', 'r') as ex_xml:

            if self.doc_type == 'waybill_v4_ip':
                self.isIp = True
            elif self.doc_type == 'waybill_v4':
                self.isIp = False
            self.doc_type = 'waybill_v4'

            if self.isIp == False:

                tree = ET.parse(ex_xml)
                root = tree.getroot()

                logger.debug(root)
                # Num
                root[1][0][0].text = str(randint(0, 9999))
                root[1][0][1][0].text = str(randint(0, 9999))
                # Date
                root[1][0][1][1].text = self.get_day()
                root[1][0][1][2].text = self.get_day()
                # alcCode
                root[1][0][2][0][1][1].text = self.product_code
                # VidCode
                root[1][0][2][0][1][2].text = self.product_vcode
                # UnitType
                if self.isUnPacked == False:
                    root[1][0][2][0][1][3].text = 'Packed'
                elif self.isUnPacked == True:
                    root[1][0][2][0][1][3].text = 'UnPacked'
                # Quantity
                root[1][0][2][0][2].text = self.quantity
                # FormA
                root[1][0][2][0][4].text = self.formA
                # FormB
                root[1][0][2][0][5][0].text = self.formB
                # mark
                root[1][0][2][0][5][1][0][1][0].text = self.bcode
            elif self.isIp == True:

                tree = ET.parse(ex_xml)
                root = tree.getroot()

                logger.debug(root)
                # Num
                root[1][0][0].text = str(randint(0, 9999))
                root[1][0][1][0].text = str(randint(0, 9999))
                # Date
                root[1][0][1][1].text = self.get_day()
                root[1][0][1][2].text = self.get_day()
                # alcCode
                root[1][0][2][0][1][1].text = self.product_code
                # VidCode
                root[1][0][2][0][1][2].text = self.product_vcode
                # UnitType
                if self.isUnPacked == False:
                    root[1][0][2][0][1][3].text = 'Packed'
                elif self.isUnPacked == True:
                    root[1][0][2][0][1][3].text = 'UnPacked'
                # Quantity
                root[1][0][2][0][2].text = self.quantity
                # FormA
                root[1][0][2][0][4].text = self.formA
                # FormB
                root[1][0][2][0][5][0].text = self.formB
                # mark
                root[1][0][2][0][5][1][0][1][0].text = self.bcode

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0][5][1][0]
                if len(position) > 1:
                    position.remove(position[1])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            return corrected_xml

    def generate_TTNinformreg(self):
        logger.debug('Генерирую xml TTNinformreg')

        with open(f'example/{self.doc_type}.xml', 'r') as ex_xml:

            tree = ET.parse(ex_xml)
            root = tree.getroot()


            logger.debug(root)
            # Num
            root[1][0][0][0].text = str(randint(0, 9999))
            # docId
            root[1][0][0][1].text = self.docId
            # FixNum
            root[1][0][0][2].text = self.fixNum
            # Date
            root[1][0][0][3].text = self.get_day()
            # WbNUM
            root[1][0][0][4].text = str(randint(0, 9999))
            # Date
            root[1][0][0][5].text = self.get_day()
            # InformF2RegId
            root[1][0][1][0][1].text = self.formB
            # Date
            root[1][0][1][0][1].text = self.get_day()

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

        conn = None
        try:
            # Подключаемся к БД
            conn = psycopg2.connect(
                dbname=self.db,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )

            logger.debug('Подключение к Postgre успешно')
            # Создаем курсор
            cursor = conn.cursor()

            logger.debug('Запрос выполняется')

            if isinstance(self.sql_req, tuple) and len(self.sql_req) == 2:
                query, params = self.sql_req
                cursor.execute(query, params)
            else:
                query = self.sql_req
                cursor.execute(query)

            if isinstance(query, str) and query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                conn.commit()
                return result
            else:
                conn.commit()
                return None

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Ошибка при работе с PostgreSQL: {error}")
            if conn:
                conn.rollback()
            return None
        finally:
            # Закрываем соединение
            if conn is not None:
                conn.close()
                logger.debug("Соединение с PostgreSQL закрыто")

    def text_to_hex(self, text_string):

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


class Outbox_checker():
    def __init__(self, db, user, password, host, port, sql_req=""):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.sql_req = sql_req

    def selecter(self, doc_uiid):
        logger.debug('Выполняю select')

        conn = None
        cursor = None

        if self.sql_req == "":
            self.sql_req = f"SELECT x.filedata FROM filedata.outboxdata AS x WHERE inboxuri = '{doc_uiid}' ORDER BY x.id DESC LIMIT 1"

        try:
            # Подключаемся к БД
            conn = psycopg2.connect(
                dbname=self.db,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logger.debug('Подключение к Postgre успешно')

            # Создаем курсор
            cursor = conn.cursor()
            query = self.sql_req
            logger.debug('Запрос выполняется')

            cursor.execute(query)

            # Получаем результаты запроса
            result = cursor.fetchall()
            conn.commit()

            if result:
                return result[0][0]
            return None

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Ошибка при работе с PostgreSQL: {error}")
            return None
        finally:
            # Закрываем соединение
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
                logger.debug("Соединение с PostgreSQL закрыто")

    def get_comment(self, doc):
        try:
            # Определяем namespace
            namespaces = {
                'ns': 'http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01',
                'tc': 'http://fsrar.ru/WEGAIS/Ticket'
            }

            # Парсим XML
            root = ET.fromstring(doc)

            # Ищем комментарий по xpath
            comment = root.find('.//tc:Comments', namespaces)

            return comment.text if comment is not None else None

        except ET.ParseError as e:
            print(f"Ошибка парсинга XML: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None


class Kafka_sender():
    def __init__(self, doc_type, uuid, topic='confirmed', docId='PRODAP-0000000000', fsrar='030000434308', inn='7841051711'):
        self.doc_type = doc_type
        self.uuid = uuid
        self.fsrar = fsrar
        self.inn = inn
        self.date = self.get_day()
        self.timezone = '+03:00'
        self.kpp = ''
        self.topic = topic
        self.docId = docId

    def json_creator(self):
        raw_message = {
            "date": self.date,
            "uri": str(self.fsrar + "-" + self.uuid),
            "type": self.doc_type,
            "DocId": self.docId
        }
        return raw_message

    def send(self):
        message = self.json_creator()

        bootstrap_server = ['test-kafka1.fsrar.ru:9092', 'test-kafka2.fsrar.ru:9092', 'test-kafka3.fsrar.ru:9092']

        producer = KafkaProducer(
            bootstrap_servers=bootstrap_server,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
        )
        producer.send(self.topic, message)
        logger.debug(f'Сообщение отправлено в топик {self.topic}')
        producer.close()

    def get_day(self):
        logger.debug('Получаю дату документа')
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        return str(formatted_date)


class Result_checker():
    def __init__(self):
        pass

    def find_message_by_uri(self, uri: str, max_attempts=3, retry_interval=10, topic='svs-inspector'):
        attempt = 0

        while attempt < max_attempts:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=['test-kafka1.fsrar.ru:9092', 'test-kafka2.fsrar.ru:9092',
                                   'test-kafka3.fsrar.ru:9092'],
                auto_offset_reset='earliest',
                consumer_timeout_ms=10000,
                value_deserializer=lambda x: self._safe_deserialize_json(x)  # Используем безопасный десериализатор
            )

            logger.debug(f"Попытка {attempt + 1} из {max_attempts}")

            try:
                for message in consumer:
                    if not message.value:  # Пропускаем None (когда десериализация не удалась)
                        continue

                    msg_value = message.value
                    if isinstance(msg_value, dict) and msg_value.get('uri') == uri:
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
        return False

    def _safe_deserialize_json(self, x):
        try:
            return json.loads(x.decode('utf-8')) if x else None
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.debug(f"Не удалось десериализовать сообщение: {e}. Сообщение будет пропущено.")
            return None

# if __name__ == "__main__":
#
#     forming = Forming_xml(doc_type='actfixbarcode')
#     forming.isMark=True
#     forming.isUnPacked = True
#     corr_xml = forming.generate_AFBC()
#     logger.debug(corr_xml)
#     logger.debug('Успех генерации xml')
