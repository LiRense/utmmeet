import os
import shutil
import uuid
from datetime import datetime,timezone
import time
import re
import subprocess
import xml.etree.ElementTree as ET
from base64 import b64encode

def connect_Docker():
    bshCmd = 'ssh DockerHub'
    process = subprocess.Popen(bshCmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               universal_newlines=True,
                               bufsize=0)
    # process.stdin.write(f"echo '{}' > cheque_v4.json\n")
    # process.stdin.write(f"echo '{}' > some_text_topic\n")
    process.stdin.write("kafkacat -P -b 10.10.4.28:9092 -t app_egaisdocfixationsign_topic < ~/some_text_topic\n")
    time.sleep(2)
    process.stdin.write("kafkacat -P -b 10.10.4.28:9092 -t app_egaisdocfixation_topic < ~/test_fix.json\n")
    process.stdin.write("exit\n")
    process.stdin.close()

def cheque_v4_maker(date,mark,volume,type):
    date_pattern = re.compile(r'\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])')
    namespace = dict(c="http://fsrar.ru/WEGAIS/Common",
                     ck="http://fsrar.ru/WEGAIS/ChequeV4",
                     ns="http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01",
                     pref="http://fsrar.ru/WEGAIS/ProductRef_v2",
                     xs="http://www.w3.org/2001/XMLSchema",
                     xsi="http://www.w3.org/2001/XMLSchema-instance"
                     )
    if re.fullmatch(date_pattern,date):
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        os.makedirs(f'/home/ivan/PycharmProjects/utmmeet/cheque_v4_sender/che4_catering/{dt_string}', exist_ok=True)

        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%H:%M:%S")

        uuidgen = uuid.uuid4()
        shutil.copyfile('che4_catering/ethalon_che4', f'che4_catering/{dt_string}/030000434308-{uuidgen}')

        parser = ET.XMLParser(encoding="utf-8")

        tree = ET.parse(f'che4_catering/{dt_string}/030000434308-{uuidgen}', parser=parser)
        tree.find('.//ck:Date',namespaces=namespace).text = f'{date}T{currentTime}'
        tree.find('.//ck:Type', namespaces=namespace).text = type
        tree.find('.//ck:Barcode', namespaces=namespace).text = str(mark)
        tree.find('.//ck:Volume', namespaces=namespace).text = str(volume)
        tree.write(f'che4_catering/{dt_string}/030000434308-{uuidgen}', encoding="utf-8")

        return f'030000434308-{uuidgen}',dt_string,date

    else:
        utc_cur_date = datetime.now(timezone.utc)
        print(str(utc_cur_date)+'   |    Кривая дата')

def base64_encoding(filename,times):
    file = open(f'che4_catering/{times}/{filename}','r')
    file_data = file.read()
    file_data = file_data.encode('utf-8')
    encoded_string = b64encode(file_data)
    # print(encoded_string)
    file.close()

def make_json(base64file,fsrar,uri,currentTime):
    ethalon = f'"certificate": "MIIJLTCCCNqgAwIBAgIQAdmpDkTfIBAABduUOB0AAjAKBggqhQMHAQEDAjCCAbQxGTAXBgkqhkiG9w0BCQEWCmNhQGllY3AucnUxXTBbBgNVBAkMVNGD0LsuINCg0LDQtNC40L4sINC00L7QvCAyNCwg0LrQvtGA0L/Rg9GBIDEsINC/0L7QvNC10YnQtdC90LjQtSBWLCDQutC+0LzQvdCw0YLQsCAyMzELMAkGA1UEBhMCUlUxHDAaBgNVBAgMEzc3INCzLiDQnNC+0YHQutCy0LAxGTAXBgNVBAcMENCzLiDQnNC+0YHQutCy0LAxMDAuBgNVBAsMJ9Cj0LTQvtGB0YLQvtCy0LXRgNGP0Y7RidC40Lkg0YbQtdC90YLRgDFYMFYGA1UECgxP0JDQutGG0LjQvtC90LXRgNC90L7QtSDQvtCx0YnQtdGB0YLQstC+ICLQkNC90LDQu9C40YLQuNGH0LXRgdC60LjQuSDQptC10L3RgtGAIjEYMBYGBSqFA2QBEg0xMTA1MjYwMDAxMTc1MRUwEwYFKoUDZAQSCjUyNjAyNzA2OTYxNTAzBgNVBAMMLNCQ0J4gItCQ0L3QsNC70LjRgtC40YfQtdGB0LrQuNC5INCm0LXQvdGC0YAiMB4XDTIzMDYyNzE1NDQwMFoXDTI0MDYyNzE1NDQwMFowggJfMS8wLQYJKoZIhvcNAQkBFiBpLm1hcnRpa2hpbkByNzcuY2VudGVyLWluZm9ybS5ydTEpMCcGA1UECQwg0KPQmy4g0J7QkdCg0JDQl9Cm0J7QktCQLCDQlC4gMzgxCzAJBgNVBAYTAlJVMS8wLQYDVQQIDCY1MCDQnNC+0YHQutC+0LLRgdC60LDRjyDQvtCx0LvQsNGB0YLRjDEYMBYGA1UEBwwP0JMu0JzQvtGB0LrQstCwMSQwIgYDVQQqDBvQmNCy0LDQvSDQkNC90LTRgNC10LXQstC40YcxGTAXBgNVBAQMENCc0LDRgNGC0LjRhdC40L0xRDBCBgNVBAwMO9CY0L3QttC10L3QtdGAINC+0YLQtNC10LvQsCDRgtC10YHRgtC40YDQvtCy0LDQvdC40Y8g0J/QotCaMW0wawYDVQQLDGTQnNCe0KHQmtCe0JLQodCa0JjQmSDQpNCY0JvQmNCQ0Jsg0JDQmtCm0JjQntCd0JXQoNCd0J7Qk9CeINCe0JHQqdCV0KHQotCS0JAgItCm0JXQndCi0KDQmNCd0KTQntCg0JwiMSYwJAYDVQQKDB3QkNCeICLQptCV0J3QotCg0JjQndCk0J7QoNCcIjEWMBQGBSqFA2QDEgsxODQxMTMxOTQ0ODEYMBYGBSqFA2QBEg0xMTc3ODQ3MDA1OTMwMRUwEwYFKoUDZAQSCjc4NDEwNTE3MTExGjAYBggqhQMDgQMBARIMNzcxMzkxOTM1MzE5MSYwJAYDVQQDDB3QkNCeICLQptCV0J3QotCg0JjQndCk0J7QoNCcIjBmMB8GCCqFAwcBAQEBMBMGByqFAwICIwEGCCqFAwcBAQICA0MABEBs/YCz6RUkb3INkFX2rlvMe1YkzaaEguDFYEPi+GWzEtpBEYXyzd5+JnZOI9VlGjoDntNMqwrVIanHAc0qpyh1gQkAMzgxRDAwMDKjggQFMIIEATAdBgNVHQ4EFgQUR905KKAhiWtaUxSFBioSn6pySNAwCwYDVR0PBAQDAgTwMB0GA1UdJQQWMBQGCCsGAQUFBwMCBggrBgEFBQcDBDBrBgUqhQNkbwRiDGDQodCa0JfQmCDCq9Ca0YDQuNC/0YLQvtGC0L7QutC10L0gMiDQrdCfwrsg0LIg0YHQvtGB0YLQsNCy0LUg0LjQt9C00LXQu9C40Y8gwqtKYUNhcnRhINCT0J7QodCiwrswDAYFKoUDZHIEAwIBADCBwwYFKoUDZHAEgbkwgbYMPFZpUE5ldCBDU1AgNC40ICjQstC10YDRgdC40Y8gNC40LjIpICjQuNGB0L/QvtC70L3QtdC90LjQtSAzKQwS0J/QmiBWaVBOZXQg0KPQpiA0DFPQodC10YDRgtC40YTQuNC60LDRgiDRgdC+0L7RgtCy0LXRgtGB0YLQstC40Y8g0KTQodCRINCg0L7RgdGB0LjQuCDihJYg0KHQpC8xMjQtNDEwMwwN0KHQpC8xMTgtMzUxMDAMBgNVHRMBAf8EAjAAMGEGCCsGAQUFBwEBBFUwUzAkBggrBgEFBQcwAYYYaHR0cDovL29jc3AuaWVjcC5ydS9vY3NwMCsGCCsGAQUFBzAChh9odHRwOi8vaWVjcC5ydS9VQ19BQy9BQzIwMjMuY3J0MF8GA1UdHwRYMFYwKaAnoCWGI2h0dHA6Ly9pZWNwLnJ1L1VDX0FDL0NPQy9BQzIwMjMuY3JsMCmgJ6AlhiNodHRwOi8vY3JsMi5ydS91Y19hYy9jb2MvYWMyMDIzLmNybDCCAXYGA1UdIwSCAW0wggFpgBR2TTFocPi4qp6IpKfBS0+Bie4j1KGCAUOkggE/MIIBOzEhMB8GCSqGSIb3DQEJARYSZGl0QGRpZ2l0YWwuZ292LnJ1MQswCQYDVQQGEwJSVTEYMBYGA1UECAwPNzcg0JzQvtGB0LrQstCwMRkwFwYDVQQHDBDQsy4g0JzQvtGB0LrQstCwMVMwUQYDVQQJDErQn9GA0LXRgdC90LXQvdGB0LrQsNGPINC90LDQsdC10YDQtdC20L3QsNGPLCDQtNC+0LwgMTAsINGB0YLRgNC+0LXQvdC40LUgMjEmMCQGA1UECgwd0JzQuNC90YbQuNGE0YDRiyDQoNC+0YHRgdC40LgxGDAWBgUqhQNkARINMTA0NzcwMjAyNjcwMTEVMBMGBSqFA2QEEgo3NzEwNDc0Mzc1MSYwJAYDVQQDDB3QnNC40L3RhtC40YTRgNGLINCg0L7RgdGB0LjQuIIKMJnLrQAAAAAHrjAnBgNVHSAEIDAeMAgGBiqFA2RxATAIBgYqhQNkcQIwCAYGKoUDZHEDMAoGCCqFAwcBAQMCA0EArU9rTljrSlkJdt+yF+PkpeK+PVkIa3JCBuolgi1Sd7VfVHpM1iMq7d/GJRowdh2bjQ+b1PaPGUHdqcLpdrOT/Q==","sign": "qTOIACl6zMneb+WyskgpFoQWXWCy88MgZUbqf6Q7Iil23PyeJrW4X2hP+B3MEKtK3OzlZk3RKtjzIVYW3geSLw==","type": "ChequeV4","data": {base64file},"date": {currentTime},"timezone": "+03:00","fsrarid": {fsrar},"uri": {uri}'
    ethalon = '{'+ethalon+'}'
    print(currentTime,uri)
    return ethalon

def put_cheque_in_mnt(name,times,currentTime):
    os.system(f'scp /home/ivan/PycharmProjects/utmmeet/cheque_v4_sender/che4_catering/{times}/{name} martikhin@DockerHub:/mnt/nfs/tmp/inbox/2024-04-09/cheques')
    # file = open(f'/home/ivan/PycharmProjects/utmmeet/cheque_v4_sender/che4_catering/{times}/{name}','r')
    # files = file.read()
    # print(files)
    bshCmd = 'ssh DockerHub'
    process = subprocess.Popen(bshCmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               universal_newlines=True,
                               bufsize=0)
    process.stdin.write(f"mkdir /mnt/nfs/tmp/inbox/{currentTime}\n")
    time.sleep(2)
    process.stdin.write(f"mkdir /mnt/nfs/tmp/inbox/{currentTime}/cheques\n")
    time.sleep(2)
    # process.stdin.write(f"echo {lines} > {name}\n")
    process.stdin.write("exit\n")
    process.stdin.close()

def write_kafka(file_b64):
    bshCmd = 'ssh DockerHub'
    process = subprocess.Popen(bshCmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               universal_newlines=True,
                               bufsize=0)
    process.stdin.write(f"echo '{file_b64}' > ~/some_text_topic\n")
    process.stdin.write(f"kafkacat -P -b test-kafka1.fsrar.ru:9092 -t inbox < ~/some_text_topic\n")
    time.sleep(2)
    process.stdin.write("exit\n")
    process.stdin.close()




start = int(input('Для отправки чека продажи >>> 1\nДля отправки чека возврата >>> 2\nEXIT >>> 0\n>>> '))

if start == 1:
    mark = input('Марка для продажи >>> ')
    volume = input('Объем продажи >>> ')
    name,times, currentTime = cheque_v4_maker('2024-04-09',mark,volume,'Продажа')
    file_b64 = base64_encoding(name,times)
    eth = make_json(file_b64, '030000434308', name, currentTime)
    print(eth)
elif start == 2:
    mark = input('Марка для возврата >>> ')
    volume = input('Объем возврата >>> ')
    name,times, currentTime = cheque_v4_maker('2024-04-04', mark, volume, 'Возврат')
    file_b64 = base64_encoding(name,times)
    eth = make_json(file_b64, '030000434308', name,currentTime)
    print(eth)

put_cheque_in_mnt(name, times, currentTime)
write_kafka(eth)
# start = int(input('Для отправки чека продажи >>> 1\nДля отправки чека возврата >>> 2\nEXIT >>> 0\n'))