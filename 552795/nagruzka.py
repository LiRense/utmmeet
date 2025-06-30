from loguru import logger
import time
import requests
from datetime import datetime

def read_errors_from_timestamp(filename, start_timestamp):
    start_time = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S,%f")
    error_blocks = []
    with open(filename, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        try:
            line_time_str = line.split()[0] + ' ' + line.split()[1]
            line_time = datetime.strptime(line_time_str, "%Y-%m-%d %H:%M:%S,%f")
            if line_time >= start_time and 'ERROR' in line:
                start_index = max(0, i - 5)
                end_index = min(len(lines), i + 31)
                error_block = lines[start_index:end_index]
                error_blocks.append(''.join(error_block))
        except (IndexError, ValueError):
            continue

    return error_blocks

logger.add("my_log_file.log", rotation="10 MB", retention="10 days")

# logger.debug("Это сообщение уровня DEBUG")
# logger.info("Это сообщение уровня INFO")
# logger.warning("Это сообщение уровня WARNING")
# logger.error("Это сообщение уровня ERROR")
# logger.critical("Это сообщение уровня CRITICAL")

logger.info('Запускаю нагрузку РусТокен')
k = 1
duration = 24 * 60 * 60  # 24 часа * 60 минут * 60 секунд (кол-во секунд в сутках)
xml_data_1 = """<?xml version="1.0" encoding="utf-8"?>
<ns:Documents Version="1" xmlns:oref="http://fsrar.ru/WEGAIS/ClientRef_v2" xmlns:rpp="http://fsrar.ru/WEGAIS/ClaimIssueFSM" xmlns:ns="http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ce="http://fsrar.ru/WEGAIS/CommonV3" xmlns:pref="http://fsrar.ru/WEGAIS/ProductRef_v2">
  <ns:Owner>
    <ns:FSRAR_ID>030000434308</ns:FSRAR_ID>
  </ns:Owner>
  <ns:Document>
    <ns:ClaimIssueFSM>
      <rpp:Identity>UTM</rpp:Identity>
      <rpp:Header>"""
xml_data_2 = """<rpp:Date>2025-05-26</rpp:Date>
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
          <rpp:alcPercent>40</rpp:alcPercent>
          <rpp:alcPercentMin>40</rpp:alcPercentMin>
          <rpp:alcPercentMax>40</rpp:alcPercentMax>
          <rpp:QuantityDal>0.0500</rpp:QuantityDal>
          <rpp:Capacity>0.5</rpp:Capacity>
          <rpp:Quantity>1</rpp:Quantity>
          <rpp:VidAP171fz>Бренди</rpp:VidAP171fz>
          <rpp:SampleFSM>ФСМ. Алкогольная продукция свыше 9%. До 0,5 л</rpp:SampleFSM>
          <rpp:MarkType>187</rpp:MarkType>
          <rpp:Identity>0</rpp:Identity>
        </rpp:Position>
      </rpp:Content>
    </ns:ClaimIssueFSM>
  </ns:Document>
</ns:Documents>"""

while k != duration:
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

    logger.info(f'Формирую xml {k}')
    xml_num = f'\n<rpp:NUMBER>{k}</rpp:NUMBER>\n'
    xml_full = xml_data_1 + xml_num + xml_data_2

    logger.info('Отправляю xml')
    headers = {
        'accept': 'text/xml',
    }
    files = {
        'xml_file': ('data.xml', xml_full, 'text/xml')
    }
    response = requests.post('http://localhost:8080/opt/in/ClaimIssueFSM', headers=headers, files=files)

    logger.debug(f'Статус документа: {response.status_code}')
    logger.debug(response.text)

    logger.info('Читаем ошибки')
    error_blocks = read_errors_from_timestamp(r'C:\UTM\transporter\l\transport_info.log', f'{formatted_time}')
    if not error_blocks:
        logger.debug('Ошибок не обнаружено')
    else:
        for block in error_blocks:
            error_lines = []
            error_line = next(line for line in block if 'ERROR' in line)
            error_lines.append(error_line.strip())
            trimmed_error_lines = [line.split('- ')[1] for line in error_lines]
            for line_s in trimmed_error_lines:
                logger.error(line_s)
            logger.debug('                    |' + block)

    k+=1

    time.sleep(1)
