from DB_toonel import RemoteMSSQLClient
import BCode_gen
from random import randint
from datetime import datetime, date
import time
import xml.etree.ElementTree as ET
from loguru import logger
import requests
import tempfile
import os
import re
import xml.dom.minidom
import json
from io import BytesIO

class minAgeSparcle():

    def __init__(self,
                 doc_type='RepProducedProduct_v4',
                 fsrar='030000434308',
                 inn='7841051711',
                 kpp='770101008',
                 pr_name='Водка СИБИРСКИЙ ВОЛК',
                 product_code='0300004343080000017',
                 capacity='1',
                 alc_percent='40',
                 product_vcode='200',
                 quantity='1',
                 ip_inn='771391935319',
                 ip_fsrar='030043434308',
                 ip_name='ИП Мартихин Иван Андреевич',
                 isUnPacked=False,
                 docId='PRODAP-0000000000',
                 isMark=True,
                 formA='TEST-FA-000000036477315',
                 formB='TEST-FB-000000041014823',
                 doc=""):
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

        self.isUnPacked = isUnPacked
        self.isMark = isMark

        self.formA = formA
        self.formB = formB

        self.doc = doc


    def get_day(self):
        logger.debug('Получаю дату документа')
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        return str(formatted_date)

    def xml_gen_choice(self, doc):
        if doc == 'RPP_v4':
            self.doc_type = 'RepProducedProduct_v4'
            self.product_code = '0300004343080000017'
            return self.RPP_v4_gen()
        elif doc == 'RPP_v5':
            self.doc_type = 'RepProducedProduct_v5'
            self.product_code = '0300004343080000017'
            return self.RPP_v5_gen()
        elif doc == 'RPP_v6':
            self.doc_type = 'RepProducedProduct_v6'
            self.product_code = '0300004343080000017'
            return self.RPP_v6_gen()
        elif doc == 'RIP_v6':
            self.doc_type = 'RepImportedProduct_v6'
            self.product_code = '0300004343080000008'
            return self.RIP_v6_gen()
        elif doc == 'RIP_v4':
            self.doc_type = 'RepImportedProduct_v4'
            self.product_code = '0300004343080000008'
            return self.RIP_v4_gen()
        elif doc == 'RIP_v5':
            self.doc_type = 'RepImportedProduct_v5'
            self.product_code = '0300004343080000008'
            return self.RIP_v5_gen()

        logger.debug('Выбрали'+self.doc)

    def db_selecter(self, query, params):

        logger.debug('Инициализирую подключение к БД')

        client = RemoteMSSQLClient(
            target_host="DockerHub",
            server_script_path="~/msSql_getter.py",
            connection_string="DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.10.4.139;DATABASE=EgaisNSI_test;UID=repp;PWD=LinkedServer123",
            target_user="martikhin"
        )

        logger.debug('Подключение успешно')
        logger.debug('Выполняю запрос')

        result = client.select(
            query,
            params
        )

        if result:

            logger.debug('Результат получен')
            return result
        else:
            logger.error('Результат отсутствует')
            return None

    def db_updater(self, query, params):
        logger.debug('Инициализирую подключение к БД')

        client = RemoteMSSQLClient(
            target_host="DockerHub",
            server_script_path="~/msSql_getter.py",
            connection_string="DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.10.4.139;DATABASE=EgaisNSI_test;UID=repp;PWD=LinkedServer123",
            target_user="martikhin"
        )

        logger.debug('Подключение успешно')
        logger.debug('Выполняю запрос')

        result = client.update(
            query,
            params
        )

        if result > 0:
            logger.debug('Изменения успешны')
            return result
        else:
            logger.error('Изменения отсутствуют')
            return None

    def gen_150_mark(self):
        logger.debug('Генерирую марку')
        number = str(randint(0, 99999999))
        number = '0' * (8 - len(number)) + number

        alk = self.product_vcode
        serial = '200'

        month = str(datetime.now().month)
        month = '0' * (2 - len(month)) + month
        year = str(datetime.now().year)[-2:]

        version = '001'

        a = BCode_gen.Generator()
        kript = BCode_gen.Generator.gen_vers(a, n=129)


        logger.debug('Марка успешно сгенерирована')
        return alk + serial + str(number) + month + year + version + kript

    def RPP_v4_gen(self):
        logger.debug('Генерирую xml')

        with open(f'docs/RPP_v4.xml', 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

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

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0][5]
                if len(position) > 0 and 'MarkInfo' in position[-1].tag:
                    position.remove(position[-1])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            logger.debug('XML успешно сгенерирована')
            return corrected_xml

    def RPP_v5_gen(self):
        logger.debug('Генерирую xml')

        with open(f'docs/RPP_v5.xml', 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

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

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0][5]
                if len(position) > 0 and 'MarkInfo' in position[-1].tag:
                    position.remove(position[-1])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            logger.debug('XML успешно сгенерирована')
            return corrected_xml

    def RIP_v6_gen(self):
        logger.debug('Генерирую xml')

        with open(f'docs/RIP_v6.xml', 'r') as ex_xml:
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
            # alcPercent
            root[1][0][2][0][2].text = self.alc_percent
            # BCode
            root[1][0][2][0][10][0].text = self.gen_150_mark()

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0][5]
                if len(position) > 0 and 'MarkInfo' in position[-1].tag:
                    position.remove(position[-1])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            logger.debug('XML успешно сгенерирована')
            return corrected_xml

    def RPP_v6_gen(self):
        logger.debug('Генерирую xml')

        with open(f'docs/RPP_v6.xml', 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

            # Num
            root[1][0][0].text = str(randint(0, 9999))
            root[1][0][1][1].text = str(randint(0, 9999))

            # FSRAR_ID
            root[0][0].text = self.fsrar
            # Date
            root[1][0][1][1].text = self.get_day()
            # ProducedDate
            root[1][0][1][2].text = self.get_day()
            # DATEOFRECEIPT
            root[1][0][2][0][9][0][3].text = self.get_day()
            # ClientRegId
            root[1][0][1][4][0][0].text = self.fsrar
            # INN
            root[1][0][1][4][0][3].text = self.inn
            # KPP
            root[1][0][1][4][0][4].text = self.kpp
            # ProductCode
            root[1][0][2][0][0].text = self.product_code
            # Quantity
            root[1][0][2][0][1].text = self.quantity
            # alcPercent
            root[1][0][2][0][3].text = self.alc_percent
            # BCode
            root[1][0][2][0][2][0].text = self.gen_150_mark()

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0][2][0]
                if len(position) > 0 and 'MarkInfo' in position[-1].tag:
                    position.remove(position[-1])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            logger.debug('XML успешно сгенерирована')
            return corrected_xml

    def RIP_v4_gen(self):
        logger.debug('Генерирую xml')

        with open(f'docs/RIP_v4.xml', 'r') as ex_xml:
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
            # alcPercent
            root[1][0][2][0][1].text = self.alc_percent
            root[1][0][2][0][2].text = self.alc_percent
            root[1][0][2][0][3].text = self.alc_percent
            # Quantity
            root[1][0][2][0][4].text = self.quantity
            # BCode
            root[1][0][2][0][11][0].text = self.gen_150_mark()

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0][5]
                if len(position) > 0 and 'MarkInfo' in position[-1].tag:
                    position.remove(position[-1])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            logger.debug('XML успешно сгенерирована')
            return corrected_xml

    def RIP_v5_gen(self):
        logger.debug('Генерирую xml')

        with open(f'docs/RIP_v5.xml', 'r') as ex_xml:
            tree = ET.parse(ex_xml)
            root = tree.getroot()

            # Num
            root[1][0][0].text = str(randint(0, 9999))
            root[1][0][1][0].text = str(randint(0, 9999))

            # FSRAR_ID
            root[0][0].text = self.fsrar
            # Date
            root[1][0][1][1].text = self.get_day()
            root[1][0][2][0][2].text = self.get_day()
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
            # alcPercent
            root[1][0][2][0][1].text = self.alc_percent
            # Quantity
            root[1][0][2][0][3].text = self.quantity
            # BCode
            root[1][0][2][0][9][0].text = self.gen_150_mark()

            if self.isMark == False:
                # BCode delete
                position = root[1][0][2][0][5]
                if len(position) > 0 and 'MarkInfo' in position[-1].tag:
                    position.remove(position[-1])

            corrected_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
            logger.debug('XML успешно сгенерирована')
            return corrected_xml

    def curl_sender_memory(self, xml):
        url = f"http://localhost:8080/opt/in/{self.doc_type}"

        try:
            # Генерируем XML
            xml_content = xml

            # Создаем файловый объект в памяти
            xml_file = BytesIO(xml_content.encode('utf-8'))

            # Подготавливаем данные для отправки
            files = {
                'xml_file': (f'{self.doc_type}.xml', xml_file, 'text/xml')
            }

            headers = {
                'accept': 'text/xml'
            }

            # Отправляем запрос
            logger.debug(f'Отправляю POST запрос на {url}')
            response = requests.post(url, files=files, headers=headers)

            # Закрываем файловый объект
            xml_file.close()

            # Проверяем ответ
            if response.status_code == 200:
                logger.success(f'Успешная отправка. Ответ: {response.text}')

                root = ET.fromstring(response.text)
                url_element = root.find('url')

                if url_element is not None:
                    file_url = url_element.text
                    logger.debug(f'Получен URL файла: {file_url}')

                    if file_url:
                        logger.success(f'Успешно получен url')
                        return file_url
                    else:
                        logger.error(f'Ошибка получения url. Код: {file_url}')
                        return None
                else:
                    logger.error('Не найден тег <url> в ответе')
                    return None
            else:
                logger.error(f'Ошибка отправки')
                return None

        except Exception as e:
            logger.error(f'Ошибка при отправке: {str(e)}')
            return None

    def result_get(self, url_id):
        logger.debug(f"Ожидаем тикеты")
        # Ждем 1 минуту перед выполнением запроса
        time.sleep(30)

        url = f"http://localhost:8080/opt/out/waybill/{url_id}"
        headers = {"accept": "text/xml"}

        while True:
            try:
                # Выполняем GET-запрос
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Проверяем статус ответа

                # print(response.content)

                # Парсим XML
                root = ET.fromstring(response.content)

                # Проверяем наличие CryptoTicket в URL элементах
                url_elements = root.findall('.//url')

                # Ищем CryptoTicket в тексте URL элементов
                crypto_ticket_found = False
                for url_element in url_elements:
                    if url_element.text and 'CryptoTicket' in url_element.text:
                        logger.debug("Обнаружен CryptoTicket в URL - требуется переотправка документа")
                        crypto_ticket_found = True
                        break

                if crypto_ticket_found:
                    # Здесь нужно вызвать метод для переотправки
                    return self.handle_crypto_ticket_retry()

                url_count = len(url_elements)

                # Логируем для отладки
                logger.debug(f"Найдено URL элементов: {url_count}")

                # Если URL нет, ждем и повторяем запрос
                if url_count == 0:
                    logger.debug("URL не найдены, повторяем запрос через 30 секунд...")
                    time.sleep(30)
                    continue

                # Если 1 тикет - возвращаем его текст
                if url_count == 1:
                    return url_elements[0].text

                # Если больше 1 тикета - находим с минимальным ID
                if url_count > 1:
                    # Извлекаем ID из URL и находим минимальный
                    min_url = None
                    min_id = float('inf')

                    for url_element in url_elements:
                        url_text = url_element.text
                        # Извлекаем числовой ID из конца URL
                        url_id = int(url_text.split('/')[-1])

                        if url_id < min_id:
                            min_id = url_id
                            min_url = url_text

                    logger.debug(f"Найден минимальный ID: {min_id}, URL: {min_url}")
                    return min_url

            except requests.exceptions.RequestException as e:
                logger.debug(f"Ошибка при выполнении запроса: {e}")
                # При ошибке сети ждем и повторяем
                time.sleep(30)
            except ET.ParseError as e:
                logger.debug(f"Ошибка при парсинге XML: {e}")
                # При ошибке парсинга ждем и повторяем
                time.sleep(30)
            except (ValueError, IndexError) as e:
                logger.debug(f"Ошибка при извлечении ID из URL: {e}")
                # При ошибке обработки URL ждем и повторяем
                time.sleep(30)

    def handle_crypto_ticket_retry(self):
        """Обработка переотправки при получении CryptoTicket"""
        try:
            logger.debug("Выполняю переотправку документа")

            xml = self.xml_gen_choice(self.doc)

            # Отправляем документ снова
            curl_res = self.curl_sender_memory(xml)

            if curl_res:
                # Рекурсивно вызываем result_get для нового URL
                return self.result_get(curl_res)
            else:
                logger.error("Не удалось переотправить документ")
                return None

        except Exception as e:
            logger.error(f"Ошибка при переотправке документа: {str(e)}")
            return None

    def ticket_get(self, address):
        logger.debug(f"Начало выполнения ticket_get. URL: {address}")

        # Выполняем GET-запрос с нужными заголовками
        headers = {'accept': 'text/xml'}
        logger.debug(f"Выполнение GET-запроса к {address} с headers: {headers}")

        response = requests.get(address, headers=headers)
        logger.debug(f"Получен ответ. Статус код: {response.status_code}")

        # Проверяем успешность запроса
        try:
            response.raise_for_status()
            logger.debug("Запрос выполнен успешно")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ошибка HTTP при запросе: {e}")
            raise

        # Получаем XML текст
        xml_text = response.text
        logger.debug(f"Получен XML текст. Длина: {len(xml_text)} символов")

        try:
            # Парсим XML
            logger.debug("Начало парсинга XML")
            root = ET.fromstring(xml_text)
            logger.debug("XML успешно распарсен")

            # Находим элемент Comments в пространстве имен tc
            namespaces = {
                'ns': 'http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01',
                'tc': 'http://fsrar.ru/WEGAIS/Ticket'
            }

            logger.debug(f"Поиск элемента Comments с namespaces: {namespaces}")
            # Ищем комментарий
            comment_element = root.find('.//tc:Comments', namespaces)

            if comment_element is not None:
                comment_text = comment_element.text
                logger.debug(f"Найден элемент Comments. Текст: {comment_text}")

                # Проверяем текст комментария
                if comment_text and 'Документ успешно принят системой на обработку' in comment_text:
                    logger.info("Документ успешно принят системой на обработку")
                    return ('Документ успешно принят системой на обработку', xml_text)
                else:
                    logger.debug(f"Комментарий не содержит ожидаемый текст. Возвращаем: {comment_text}")
                    return (comment_text, xml_text)
            else:
                # Если элемент Comments не найден, возвращаем весь XML
                logger.warning("Элемент Comments не найден в XML")
                return ('Комментарий не найден в XML', xml_text)

        except ET.ParseError as e:
            # Если XML невалидный, возвращаем ошибку парсинга
            logger.error(f"Ошибка парсинга XML: {e}")
            return ('Ошибка парсинга XML', xml_text)
        except Exception as e:
            logger.error(f"Неожиданная ошибка при обработке XML: {e}")
            return ('Ошибка обработки XML', xml_text)

    def result_interpretation(self, data_string):
        # Преобразуем строку в словарь
        if isinstance(data_string, str):
            data = json.loads(data_string)
        else:
            data = data_string

        # Функция для форматирования XML
        def pretty_xml(xml_string):
            if not xml_string:
                return ""
            try:
                parsed = xml.dom.minidom.parseString(xml_string)
                return parsed.toprettyxml(indent="    ")
            except:
                return xml_string

        # Извлекаем данные
        num_days = data.get('num_days', '')
        okpd2 = data.get('OKPD2', '')
        code_vid_egais = data.get('CodeVidEgais', '')
        nsi_data = data.get('nsi_data', '')
        doc_xml = data.get('doc_xml', '')
        ticket_xml = data.get('ticket_xml', '')
        expected = data.get('expected', '')
        obtained = data.get('obtained', '')

        # Если ticket_xml - это кортеж, берем второй элемент (XML)
        if isinstance(ticket_xml, tuple) and len(ticket_xml) > 1:
            ticket_xml = ticket_xml[1]

        # Формируем строку отчета
        report_lines = []

        # Первая строка с основной информацией
        report_lines.append(f"# MinAgeFortWine = {num_days}, ОКПД2 = {okpd2} ({code_vid_egais})")

        # Блок NSI_Product (если есть данные)
        if nsi_data:
            report_lines.append("{{collapse(NSI_Product)")
            report_lines.append("<pre>")
            report_lines.append(str(nsi_data))
            report_lines.append("</pre>")
            report_lines.append("}}")

        # Блок doc XML
        report_lines.append("{{collapse(doc)")
        report_lines.append("<pre>")
        if doc_xml:
            report_lines.append(pretty_xml(doc_xml))
        report_lines.append("</pre>")
        report_lines.append("}}")

        # Блок ticket XML
        report_lines.append("{{collapse(ticket)")
        report_lines.append("<pre>")
        if ticket_xml:
            report_lines.append(pretty_xml(ticket_xml))
        report_lines.append("</pre>")
        report_lines.append("}}")

        # Результаты
        report_lines.append(f"*Ожидаемый результат: {expected}*")
        report_lines.append(f"*Полученный результат: {obtained}*")
        report_lines.append("")

        # Записываем в файл (дописываем, а не перезаписываем)
        with open("report.txt", "a", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        return "\n".join(report_lines)

    def get_comment(self, xml_content):
        """
        Извлекает содержимое комментария из XML документа

        Args:
            xml_content (str): XML строка с документом

        Returns:
            str: Содержимое комментария или пустая строка если не найден
        """
        try:
            from xml.etree import ElementTree as ET

            root = ET.fromstring(xml_content)

            # Определяем пространства имен
            namespaces = {
                'ns': 'http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01',
                'tc': 'http://fsrar.ru/WEGAIS/Ticket'
            }

            # Более конкретный путь к элементу Comments
            comment_element = root.find('.//ns:Document/ns:Ticket/tc:Result/tc:Comments', namespaces)

            if comment_element is not None and comment_element.text:
                return comment_element.text.strip()
            else:
                return ""

        except ET.ParseError as e:
            print(f"Ошибка парсинга XML: {e}")
            return ""
        except Exception as e:
            print(f"Ошибка при извлечении комментария: {e}")
            return ""


def tests_reader(file_path):
    result = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line.startswith('#'):
                continue

            # Убираем комментарий и разбиваем строку
            parts = line[1:].strip().split(', ')

            if len(parts) >= 4:
                # Обработка random()
                if parts[3].startswith('random('):
                    match = re.search(r'random\((\d+),\s*(\d+)\)', parts[3])
                    if match:
                        num_days = str(randint(int(match.group(1)), int(match.group(2))))
                    else:
                        num_days = None
                else:
                    num_days = parts[3]

                result.append({
                    "doc": parts[0],
                    "expected": parts[1],
                    "OKPD2": parts[2],
                    "num_days": num_days,
                    "obtained":"",
                    "doc_xml":"",
                    "ticket_xml":"",
                    "nsi_data":"",
                    "CodeVidEgais":""
                })

    return result

if __name__ == "__main__":

    open('report.txt', 'w')

    tests = tests_reader("RPP_v4_test_2")

    for i in tests:
        age = minAgeSparcle()
        xml = age.xml_gen_choice(i['doc'])

        i['num_days'] = None if i['num_days'] == 'NULL' else i['num_days']

        CodeVid_egais = age.db_selecter("SELECT x.CodeVid_egais FROM EgaisNSI_test.dbo.Product_Vid2021 AS x WHERE CodeVid_classifier = ?",{"0":i["OKPD2"]})
        # print({"0":CodeVid_egais[0]['CodeVid_egais'], "1": i['num_days'], "2":age.product_code})
        update_product = age.db_updater("UPDATE EgaisNSI_test.dbo.Products SET CodeVid_egais = ?, minage = ? WHERE Alc_Code = ?",{"0":CodeVid_egais[0]['CodeVid_egais'], "1": i['num_days'], "2":age.product_code})
        nsi_data = age.db_selecter(
            "SELECT x.* FROM EgaisNSI_test.dbo.Products AS x WHERE Alc_Code = ?",
            {"0": age.product_code})

        time.sleep(1)

        i['nsi_data'] = nsi_data
        i['CodeVidEgais'] = CodeVid_egais[0]['CodeVid_egais']
        logger.debug(f'Генерируем xml {i["doc"]}')
        xml = age.xml_gen_choice(i['doc'])
        age.doc = i['doc']
        i['doc_xml'] = xml

        curl_res = age.curl_sender_memory(xml)

        if curl_res:
            address = age.result_get(curl_res)
            ticket_data = age.ticket_get(address)

            i['ticket_xml'] = ticket_data
            i['obtained'] = ticket_data[0]

        age.result_interpretation(i)




