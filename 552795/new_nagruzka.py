from loguru import logger
import time
import requests
from datetime import datetime
import os
import sys
import re
from typing import List, Optional

# Настройка логирования
logger.remove()  # Удаляем стандартный обработчик
logger.add(
    "script_log.log",
    rotation="10 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
    level="INFO"
)


def is_valid_timestamp_line(line: str) -> bool:
    """
    Проверяет, является ли строка валидной временной меткой лога

    Args:
        line: строка для проверки

    Returns:
        True если строка содержит валидный формат временной метки
    """
    # Паттерн для временной метки: 2025-10-09 17:18:35,123
    timestamp_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
    return bool(re.match(timestamp_pattern, line.strip()))


def safe_datetime_parse(timestamp_str: str, format_str: str) -> Optional[datetime]:
    """Безопасное преобразование строки в datetime"""
    try:
        return datetime.strptime(timestamp_str, format_str)
    except ValueError as e:
        logger.debug(f"Не удалось преобразовать timestamp '{timestamp_str}': {e}")
        return None


def read_errors_from_timestamp(filename: str, start_timestamp: str) -> List[str]:
    """
    Чтение ошибок из файла логов начиная с указанного времени

    Args:
        filename: путь к файлу логов
        start_timestamp: начальная временная метка

    Returns:
        Список блоков с ошибками
    """
    start_time = safe_datetime_parse(start_timestamp, "%Y-%m-%d %H:%M:%S,%f")
    if not start_time:
        logger.error(f"Некорректный формат временной метки: {start_timestamp}")
        return []

    error_blocks = []

    try:
        # Проверяем существование файла
        if not os.path.exists(filename):
            logger.error(f"Файл логов не найден: {filename}")
            return []

        # Проверяем доступность файла
        if not os.access(filename, os.R_OK):
            logger.error(f"Нет прав на чтение файла: {filename}")
            return []

        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            try:
                # Пропускаем строки, которые не содержат валидную временную метку
                if not is_valid_timestamp_line(line):
                    continue

                # Извлекаем временную метку из начала строки
                line_time_str = ' '.join(line.split()[:2])  # Берем первые 2 части (дата и время)
                line_time = safe_datetime_parse(line_time_str, "%Y-%m-%d %H:%M:%S,%f")

                if line_time and line_time >= start_time and 'ERROR' in line:
                    start_index = max(0, i - 5)  # 5 строк до ошибки
                    end_index = min(len(lines), i + 31)  # 30 строк после ошибки
                    error_block = lines[start_index:end_index]
                    error_blocks.append(''.join(error_block))

            except (IndexError, ValueError, Exception) as e:
                logger.debug(f"Ошибка обработки строки {i}: {e}")
                continue

    except IOError as e:
        logger.error(f"Ошибка чтения файла {filename}: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении логов: {e}")

    return error_blocks


def send_xml_request(xml_data: str, attempt: int = 1) -> bool:
    """
    Отправка XML документа с повторными попытками

    Args:
        xml_data: XML данные для отправки
        attempt: номер текущей попытки

    Returns:
        True если отправка успешна, False в противном случае
    """
    max_retries = 1
    retry_delay = 1  # секунды

    try:
        headers = {
            'accept': 'text/xml',
            'User-Agent': 'RusToken-Load-Test/1.0'
        }
        files = {
            'xml_file': ('data.xml', xml_data, 'text/xml')
        }

        logger.info(f"Попытка {attempt} отправки XML")
        response = requests.post(
            'http://localhost:8080/opt/in/ClaimIssueFSM',
            headers=headers,
            files=files,
            timeout=60  # таймаут 30 секунд
        )

        response.raise_for_status()  # Вызовет исключение для статусов 4xx/5xx

        logger.debug(f"Статус документа: {response.status_code}")
        if response.text:
            logger.debug(f"Ответ сервера: {response.text[:200]}...")  # Логируем только начало ответа

        return True

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Ошибка подключения (попытка {attempt}): {e}")
    except requests.exceptions.Timeout as e:
        logger.error(f"Таймаут подключения (попытка {attempt}): {e}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP ошибка (попытка {attempt}): {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Статус код: {e.response.status_code}")
            logger.error(f"Тело ответа: {e.response.text[:500]}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса (попытка {attempt}): {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке XML (попытка {attempt}): {e}")

    # Повторная попытка
    if attempt < max_retries:
        logger.info(f"Повторная попытка через {retry_delay} секунд...")
        time.sleep(retry_delay)
        return send_xml_request(xml_data, attempt + 1)

    return False


def process_error_blocks(error_blocks: List[str]) -> None:
    """Обработка и логирование блоков с ошибками"""
    if not error_blocks:
        logger.debug("Ошибок не обнаружено")
        return

    try:
        for block in error_blocks:
            error_lines = []

            # Ищем строки с ERROR
            for line in block.split('\n'):
                if 'ERROR' in line and is_valid_timestamp_line(line):
                    error_lines.append(line.strip())

            if error_lines:
                # Извлекаем только сообщение об ошибке (после временной метки)
                trimmed_error_lines = []
                for line in error_lines:
                    parts = line.split(' - ', 1)
                    if len(parts) > 1:
                        trimmed_error_lines.append(parts[1])
                    else:
                        trimmed_error_lines.append(line)

                for error_msg in trimmed_error_lines:
                    logger.error(f"Обнаружена ошибка: {error_msg}")

                logger.debug(f"Полный блок ошибки:\n{block}")

    except Exception as e:
        logger.error(f"Ошибка обработки блока ошибок: {e}")


def main():
    """Основная функция выполнения скрипта"""
    logger.info('Запускаю нагрузку РусТокен')

    # Конфигурация
    DURATION = 24 * 60 * 60  # 24 часа в секундах
    LOG_FILE_PATH = r'/opt/utm/transport/l/transport_info.log'
    SLEEP_INTERVAL = 0  # секунда между итерациями
    SLEEP_INTERVAL_colv = 10
    SLEEP_INTERVAL_Pach = 10

    # Проверка доступности файла логов на старте
    if not os.path.exists(LOG_FILE_PATH):
        logger.warning(f"Файл логов {LOG_FILE_PATH} не существует. Проверка ошибок будет пропущена.")

    # XML шаблоны
    xml_data_1 = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<ns:Documents xmlns:ce="http://fsrar.ru/WEGAIS/CommonV3" xmlns:ns="http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01" xmlns:oref="http://fsrar.ru/WEGAIS/ClientRef_v2" xmlns:pref="http://fsrar.ru/WEGAIS/ProductRef_v2" xmlns:rpp="http://fsrar.ru/WEGAIS/ClaimIssueFSM" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="1">
  <ns:Owner>
    <ns:FSRAR_ID>030000434308</ns:FSRAR_ID>
  </ns:Owner>
  <ns:Document>
    <ns:ClaimIssueFSM>
      <rpp:Identity>UTM</rpp:Identity>
      <rpp:Header>"""

    xml_data_2 = """<rpp:Date>2025-10-09</rpp:Date>
        <rpp:ReportUseAutoProcess>Отчет об использовании ФСМ прошу автоматически сформировать на основе данных, зафиксированных заявителем в ЕГАИС расчетным путем.</rpp:ReportUseAutoProcess>
        <rpp:TerrOrganRAR>
          <oref:UL>
            <oref:ClientRegId>090000000001</oref:ClientRegId>
            <oref:INN>7710757158</oref:INN>
            <oref:KPP>771001001</oref:KPP>
            <oref:FullName>МЕЖРЕГИОНАЛЬНОЕ УПРАВЛЕНИЕ ФЕДЕРАЛЬНОЙ СЛУЖБЫ ПО КОНТРОЛЮ ЗА АЛКОГОЛЬНЫМ И ТАБАЧНЫМ РЫНКАМИ ПО ЦЕНТРАЛЬНОМУ ФЕДЕРАЛЬНОМУ ОКРУГУ</oref:FullName>
            <oref:address_ur>
              <oref:Country>643</oref:Country>
              <oref:RegionCode>77</oref:RegionCode>
              <oref:description>123022, г.Москва, ул. Б.Декабрьская, д.7 стр.3</oref:description>
            </oref:address_ur>
            <oref:address>
              <oref:Country>643</oref:Country>
              <oref:RegionCode>77</oref:RegionCode>
              <oref:description>125412, г. Москва, Коровинское шоссе, 43, стр. 1</oref:description>
            </oref:address>
          </oref:UL>
        </rpp:TerrOrganRAR>
        <rpp:Declarer>
          <oref:UL>
            <oref:ClientRegId>030000434308</oref:ClientRegId>
            <oref:INN>7841051711</oref:INN>
            <oref:KPP>770101008</oref:KPP>
            <oref:FullName>АКЦИОНЕРНОЕ ОБЩЕСТВО "ЦЕНТРИНФОРМ"</oref:FullName>
            <oref:address_ur>
              <oref:Country>643</oref:Country>
              <oref:RegionCode>77</oref:RegionCode>
              <oref:description>Россия, 191123,САНКТ-ПЕТЕРБУРГ Г,ШПАЛЕРНАЯ УЛ,ДОМ 26 ,</oref:description>
            </oref:address_ur>
            <oref:address>
              <oref:Country>643</oref:Country>
              <oref:RegionCode>77</oref:RegionCode>
              <oref:description>Россия,117105,Москва Г, Варшавское ш, д. 37 А, стр. 8</oref:description>
            </oref:address>
          </oref:UL>
        </rpp:Declarer>
        <rpp:TypeClaimM>
          <rpp:TypeClaim1>
            <rpp:TypeClaim>1</rpp:TypeClaim>
          </rpp:TypeClaim1>
        </rpp:TypeClaimM>
      </rpp:Header>
      <rpp:Content>
        <rpp:Position>
          <rpp:alcPercent>45</rpp:alcPercent>
          <rpp:alcPercentMin>45</rpp:alcPercentMin>
          <rpp:alcPercentMax>45</rpp:alcPercentMax>
          <rpp:QuantityDal>0.1140</rpp:QuantityDal>
          <rpp:Capacity>0.57</rpp:Capacity>
          <rpp:Quantity>2</rpp:Quantity>
          <rpp:VidAP171fz>Бренди</rpp:VidAP171fz>
          <rpp:SampleFSM>ФСМ. Алкогольная продукция свыше 9%. До 0,75 л</rpp:SampleFSM>
          <rpp:MarkType>188</rpp:MarkType>
          <rpp:Identity>0</rpp:Identity>
        </rpp:Position>
      </rpp:Content>
    </ns:ClaimIssueFSM>
  </ns:Document>
</ns:Documents>"""

    k = 1
    start_time = time.time()
    ll = 0

    try:
        while k <= DURATION:
            iteration_start = time.time()

            try:
                # Текущее время для отслеживания ошибок
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

                logger.info(f'Формирую XML документ #{k}')
                xml_num = f'\n<rpp:NUMBER>{k}</rpp:NUMBER>\n'
                xml_full = xml_data_1 + xml_num + xml_data_2

                # Отправка XML с обработкой ошибок
                success = send_xml_request(xml_full)
                if not success:
                    logger.error(f"Не удалось отправить XML документ #{k} после всех попыток")
                else:
                    logger.info(f"XML документ #{k} успешно отправлен")

                # Проверка ошибок в логах
                logger.info('Проверяем логи на наличие ошибок')
                error_blocks = read_errors_from_timestamp(LOG_FILE_PATH, formatted_time)
                process_error_blocks(error_blocks)

            except KeyboardInterrupt:
                logger.info("Получен сигнал прерывания. Завершаем работу...")
                break
            except Exception as e:
                logger.error(f"Критическая ошибка в итерации {k}: {e}")
                # Продолжаем выполнение несмотря на ошибку

            # Прогресс выполнения
            if k % 60 == 0:  # Каждую минуту
                elapsed = time.time() - start_time
                logger.info(
                    f"Прогресс: {k}/{DURATION} итераций завершено ({k / DURATION * 100:.1f}%), прошло {elapsed / 60:.1f} минут")

            k += 1

            # Точный sleep для поддержания частоты
            iteration_time = time.time() - iteration_start
            sleep_time = max(0, SLEEP_INTERVAL - iteration_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            if ll == SLEEP_INTERVAL_colv:
                time.sleep(SLEEP_INTERVAL_Pach)
                ll = 0
            else:
                ll += 1

    except Exception as e:
        logger.critical(f"Критическая ошибка выполнения скрипта: {e}")
        raise

    logger.info(f"Нагрузка завершена. Выполнено {k - 1} итераций")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}")
        sys.exit(1)