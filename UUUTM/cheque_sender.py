import os
import base64
import uuid
import subprocess

def cheque(mark):
    new_lines = []
    with open('cheques/Che.xml','r') as file:
        lines = file.readlines()
    for info in lines:
        if info == 'shable\n':
            new_lines.append('<Bottle barcode="'+mark+'" price="500.00" volume="1.0000"/>')
        else:
            new_lines.append(info)
    with open('cheques/Che_new.xml','w') as end_file:
        for item in new_lines:
            end_file.write(item)

    rmSendCommand = 'scp /home/ivan/PycharmProjects/utmmeet/UUUTM/cheques/Che_new.json' + ' martikhin@DockerHub:~/Che_new.json'
    rmSend = os.popen(rmSendCommand)

    # Мда, это не курлом, явно
    # with open('cheques/Che_new.xml','r') as end_file2:
    #     data = end_file2.read()
    # base = base64.b64encode(data.encode('utf-8'))
    # base = base.decode('utf-8')
    # json1 = {"certificate" : "","sign" : "","type" : "Cheque","data" : "","date" : "2023-07-27","timezone" : "+03:00","fsrarid" : "030000434308","uri" : "030000434308-539c05c3-f12c-403e-a19a-733329af2c16"}
    # json1['data'] = base
    # json1['uri'] = '030000434308-'+ str(uuid.uuid4())
    # json1 = str(json1)
    # with open('cheques/Che_new.json','w') as end_file2:
    #     end_file2.write(json1)
    #
    # print('SUCCESS: JSON сформирован')
    #
    # rmSendCommand = 'scp /home/ivan/PycharmProjects/utmmeet/UUUTM/cheques/Che_new.json' + ' martikhin@DockerHub:~/Che_new.json'
    # rmSend = os.popen(rmSendCommand)
    # print('SUCCESS: JSON перенесен на тестовый контур')
    #
    # bshCmd = 'ssh DockerHub'
    # process = subprocess.Popen(bshCmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    #                            universal_newlines=True,
    #                            bufsize=0)
    # process.stdin.write("kafkacat -P -b test-kafka1.fsrar.ru:9092 -t inbox < ~/Che_new.json\n")
    # process.stdin.write("exit\n")
    # process.stdin.close()
    # print('SUCCESS: JSON отправлен')


os.system("clear")
choose = input('\n1 - cheque\n2 - cheque_v3\n3 - cheque_v4\n0 - exit \n----------------------------------\n>>> ')
while choose != '0':
    os.system("clear")
    if choose == '1':
        os.system("clear")
        mark = input('\nВведите марку\n>>> ')
        os.system("clear")
        if len(mark) == 150:
            cheque(mark)
            print('SUCCESS: Файл отправлен')
        else:
            print('ERROR: Марка меньше 150 символов')
    elif choose == '2':
        pass
    elif choose == '3':
        pass
    choose = input('\n1 - cheque\n2 - cheque_v3\n3 - cheque_v4\n0 - exit \n----------------------------------\n>>> ')


