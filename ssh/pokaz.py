import json
import os
import psycopg2
import sshtunnel
import paramiko
import random
import time
import test_srez
import subprocess


def ran(sim):
    b=''
    for i in range(sim):
        a = str(random.randint(1, 9))
        b += a
    return b


# def bd():
#     try:
#
#         # пытаемся подключиться к базе данных
#         with psycopg2.connect(host='10.10.4.172',port='5432',dbname='docs', user='ci', password='ci') as conn:
#             print("Connecting")
#             try:
#                 cursor = conn.cursor()
#                 cursor.execute('SELECT transportid  FROM actwriteoff order by id desc limit 1')# Получаем список всех пользователей
#                 AWO_transp = cursor.fetchall()
#                 cursor.close()  # закрываем курсор
#                 conn.close()  # закрываем соединение
#
#                 print(AWO_transp)
#
#
#             except:
#                 print("Someting wrong")
#     except:
#         # в случае сбоя подключения будет выведено сообщение в STDOUT
#         print('Can`t establish connection to database')

# params = {
#     'PG_DB_NAME': 'docs',
#     'PG_UN': 'ci',
#     'PG_DB_PW': 'ci',
#     'DB_HOST': '10.10.4.172',
#     'LOCALHOST': '127.0.0.1',
#     'PORT': '5432',
#     'SSH_PKEY': '/home/ivan/.ssh/id_rsa',
#     'SSH_HOST': '10.0.50.208'
# }
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
            cursor1 = conn.cursor()
            cursor1.execute('SELECT *  FROM actwriteoff order by id desc limit 1')# Получаем список всех пользователей
            AWO_transp = cursor1.fetchall()
            cursor1.close()  # закрываем курсор
            print(AWO_transp)

            conn.close()
            server.close()
            print("closed all")
            return AWO_transp
    except:
        print("Connection failed")

def getDock(AWO):
    passw = 'vfhnb[by_240]'
    print(AWO[0],AWO[1])
    os.system(f'scp martikhin@DockerHub:/mnt/nfs/tmp/inbox/{AWO[0]}/actwriteoff_v3/{AWO[1]} ~/PycharmProjects/utmmeet/write_v3')

    with open(f"write_v3/{AWO[1]}", 'r') as doc:
        doc_in_list = doc.readlines()
    nums = random.randint(1,6)
    dint = '0'*nums + ran((10-nums))
    dint = 'EGAISFixNumber-'+str(dint)
    names = {'identity':'','docNumber':'','docDate':'','egaisFixNumber':dint,'reason':'Custom request','reasonCode':'0000000004'}
    stroke = [13,15,16]
    j = list()
    for i in stroke:
        s = doc_in_list[i]
        s = s[(s.find('>') + 1):]
        s = s[0:s.find('</')]
        j.append(s)
    name = ['identity','docNumber','docDate']
    for d in range(len(name)):
        names[name[d]] = j[d]
    print(names)
    return names


def conn_to_send(data):
    new = '[]'
    data_s = str(data).replace("'",'"')
    test_srez.send()
    host = '10.10.4.32'
    bshCmd = 'ssh DockerHub'
    process = subprocess.Popen(bshCmd.split(), stdin=subprocess.PIPE, stdout = subprocess.PIPE,
                               universal_newlines=True,
                               bufsize=0)
    process.stdin.write(f"echo '{data_s}' > test_fix.json\n")
    process.stdin.write(f"echo '{new}' > some_text_topic\n")
    process.stdin.write("kafkacat -P -b 10.10.4.28:9092 -t app_egaisdocfixationsign_topic < ~/some_text_topic\n")
    time.sleep(2)
    process.stdin.write("kafkacat -P -b 10.10.4.28:9092 -t app_egaisdocfixation_topic < ~/test_fix.json\n")
    process.stdin.write("exit\n")
    process.stdin.close()

    for line in process.stdout:
        if line == "END\n":
            break
        print(line, end="")
def conn_to_send2(data):
    new = '["ActWriteOff_v3"]'
    data_s = str(data).replace("'",'"')
    test_srez.send()
    host = '10.10.4.32'
    bshCmd = 'ssh DockerHub'
    process = subprocess.Popen(bshCmd.split(), stdin=subprocess.PIPE, stdout = subprocess.PIPE,
                               universal_newlines=True,
                               bufsize=0)
    process.stdin.write(f"echo '{data_s}' > test_fix.json\n")
    time.sleep(2)
    process.stdin.write(f"echo '{new}' > some_text_topic\n")
    process.stdin.write("kafkacat -P -b 10.10.4.28:9092 -t app_egaisdocfixationsign_topic < ~/some_text_topic\n")
    time.sleep(2)
    process.stdin.write("kafkacat -P -b 10.10.4.28:9092 -t app_egaisdocfixation_topic < ~/test_fix.json\n")
    process.stdin.write("exit\n")
    process.stdin.close()
#
    for line in process.stdout:
        if line == "END\n":
            break
        print(line, end="")



a = input("1 ЭП\n2 Без ЭП\n>>> ")
if  a == '1':
    AWO_transp = bd()
    # AWO_transp = [(24, 30000504835, '49', '2023-06-21', 'Проверки', 64210, 'c347829a-efe1-47a6-a894-f637f847763b')]
    AWO_uri = f"030000504835-{AWO_transp[0][6]}"
    regID = 'TEST-WOF-'+(10-len(str(AWO_transp[0][5])))*'0'+str(AWO_transp[0][5])
    AWO = [AWO_transp[0][3],AWO_uri]
    dockss = getDock(AWO)
    print(AWO_uri)
    text = '''{"docInfo": {"uri": "030000504835-99e845bf-9eab-442b-a27a-b57c7c56bc49","identity": "58",
                        "docRegId": "TEST-FB-000000040956531","docNumber": "58","docDate": "2023-06-20","docType": "UL",
                        "client": {"type": "UL","clientRegId": "030000504835","fullName": "АКЦИОНЕРНОЕ ОБЩЕСТВО ЦЕНТРИНФОРМ",
                                   "shortName": "АКЦИОНЕРНОЕ ОБЩЕСТВО ЦЕНТРИНФОРМ","inn": "7841051711","kpp": "246343001",
                                   "address": {"country": "643","regionCode": "77","description": "660028,РОССИЯ,,,КРАСНОЯРСК Г,,ТЕЛЕВИЗОРНАЯ УЛ,ДОМ 1,СТРОЕНИЕ 9,"}}},
            "result": {"fixInfo": {"egaisFixNumber": "EGAISFixNumber-008","egaisFixDate": "2022-01-01"},"denyInfo": {"reasonCode": "00001","reason": "For test"}}}'''

    data = json.loads(text)
    data['docInfo']['uri'] = AWO_uri
    data['docInfo']['identity'] = dockss['identity']
    data['docInfo']['docRegId'] = regID
    data['docInfo']['docNumber'] = dockss['docNumber']
    data['docInfo']['docDate'] = dockss['docDate']
    data['result']['fixInfo']['egaisFixNumber'] = dockss['egaisFixNumber']
    data['result']['fixInfo']['egaisFixDate'] = dockss['docDate']
    data['docInfo']['docType'] = "ActWriteOff_v3"
    data['result']['denyInfo']['reasonCode'] = dockss['reasonCode']
    data['result']['denyInfo']['reason'] = dockss['reason']
    print(data)
    file_w = open('test_fix.json', "w")
    file_w.seek(0)
    file_w.write(str(data).replace("'",'"'))
    conn_to_send(data)
elif a == '2':
    AWO_transp = bd()
    # AWO_transp = [(24, 30000504835, '49', '2023-06-21', 'Проверки', 64210, 'c347829a-efe1-47a6-a894-f637f847763b')]
    AWO_uri = f"030000504835-{AWO_transp[0][6]}"
    regID = 'TEST-WOF-' + (10 - len(str(AWO_transp[0][5]))) * '0' + str(AWO_transp[0][5])
    AWO = [AWO_transp[0][3], AWO_uri]
    dockss = getDock(AWO)
    print(AWO_uri)
    text = '''{"docInfo": {"uri": "030000504835-99e845bf-9eab-442b-a27a-b57c7c56bc49","identity": "58",
                        "docRegId": "TEST-FB-000000040956531","docNumber": "58","docDate": "2023-06-20","docType": "UL",
                        "client": {"type": "UL","clientRegId": "030000504835","fullName": "АКЦИОНЕРНОЕ ОБЩЕСТВО ЦЕНТРИНФОРМ",
                                   "shortName": "АКЦИОНЕРНОЕ ОБЩЕСТВО ЦЕНТРИНФОРМ","inn": "7841051711","kpp": "246343001",
                                   "address": {"country": "643","regionCode": "77","description": "660028,РОССИЯ,,,КРАСНОЯРСК Г,,ТЕЛЕВИЗОРНАЯ УЛ,ДОМ 1,СТРОЕНИЕ 9,"}}},
            "result": {"fixInfo": {"egaisFixNumber": "EGAISFixNumber-008","egaisFixDate": "2022-01-01"},"denyInfo": {"reasonCode": "00001","reason": "For test"}}}'''

    data = json.loads(text)
    data['docInfo']['uri'] = AWO_uri
    data['docInfo']['identity'] = dockss['identity']
    data['docInfo']['docRegId'] = regID
    data['docInfo']['docNumber'] = dockss['docNumber']
    data['docInfo']['docDate'] = dockss['docDate']
    data['result']['fixInfo']['egaisFixNumber'] = dockss['egaisFixNumber']
    data['result']['fixInfo']['egaisFixDate'] = dockss['docDate']
    data['docInfo']['docType'] = "ActWriteOff_v3"
    data['result']['denyInfo']['reasonCode'] = dockss['reasonCode']
    data['result']['denyInfo']['reason'] = dockss['reason']
    print(data)
    file_w = open('test_fix.json', "w")
    file_w.seek(0)
    file_w.write(str(data).replace("'", '"'))
    conn_to_send2(data)

