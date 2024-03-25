import os
from datetime import datetime,timezone
import shutil
from zipfile import ZipFile
from other.find_sp2 import masking_sp, masking_backbone
import time
from alive_progress import alive_bar
from PyQt5 import QtCore, QtWidgets, QtGui
import sys
from glob import glob




# os.system('dpkg -s u-trans')
# sleep(0.5)
global datas
global sp
global data2
try:
    sp = masking_sp()
    print(sp)
except FileNotFoundError:
    print("Не забудте установить УТМ")
    sp = None
except:
    sp =None

passw = input("Введите ваш пароль\n>>> ")

def check_status_utm(tqdm=None):
    start_check = datetime.now(timezone.utc) - 1
    progress_bar = tqdm.trange(10)
    for i in progress_bar:
        time.sleep(.1)
        progress_bar.write("loop %i" % i)
def update_settings():
    global datas
    global sp
    datas = {'dumbs_BD':'/home/ivan/Загрузки/utmDB/',
             'old_path':f'/opt/utm/transport/lib/',
             'project_path':'/home/ivan/PycharmProjects/utmmeet/UUUTM/',
             'sp':f'{sp}'}
def clear_utm():
    utc_cur_date = datetime.now(timezone.utc)
    dat = (str(utc_cur_date)[0:19])
    dat = dat.replace(" ","_")
    dat = dat.replace(":", "-")
    spis = [f"mkdir {datas['dumbs_BD']}",
            f'echo {passw} | sudo -S cp -r /opt/utm/transport/transportDB {datas["dumbs_BD"]}transportDB{dat}',
            f"echo {passw} | sudo -S dpkg --purge u-trans",
            f'echo {passw} | sudo -S rm -r /opt/utm/',
            f'echo {passw} | sudo -S rm -r /opt/utm/']
    with alive_bar(len(spis)) as bar:
        for i in spis:
            os.system(i)
            bar()
    filen = open('save_conf/last_prop.txt','w')
    filen.close()

def start_backbone():
    global backbone_zip
    global backbone_jar
    backbone = masking_backbone()
    print(backbone)
    backbone_zip = backbone + '.zip'
    backbone_jar = backbone + '.jar'

def install_utm():
    # os.system(f'echo {passw} | sudo -S dpkg --add-architecture i386')
    # os.system(f'echo {passw} | sudo -S apt-get install libc6:i386 libncurses5:i386 libstdc++6:i386 libssl1.1:i386')
    # os.system(f'echo {passw} | sudo -S  apt-get update')
    # os.system(f'echo {passw} | sudo -S  apt-get install pcscd')
    # os.system(f'echo {passw} | sudo -S  apt-get install libpcsclite1:i386')
    # os.system(f'echo {passw} | sudo -S  apt install acl')
    # os.system(f'echo {passw} | sudo -S  apt-get install supervisor')
    prg = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QFileDialog
    global data2
    data = dialog.getOpenFileUrl(None,caption="select file")[0].path()
    data2 = data
    file = open('save_conf/reinstal.txt', 'w')
    file.write('data '+data)
    file.close()
    # sys.exit(prg.exec_())
    print(data2)
    if data2 != "":
        os.system(f'echo {passw} | sudo -S  dpkg --install {data}')
        time.sleep(30)
    else:
        print("not file")



def jacarta_chage(id):
    file = open('save_conf/last_prop.txt', 'w')
    if id == 1:
        os.system(f'echo {passw} | sudo -S cp {datas["project_path"]}save_conf/transport_fiz.properties '
                  f'/opt/utm/transport/conf/transport.properties')
        print("Обрабатываю для физика")
        file.write('fiz')
        file.close()
    elif id == 2:
        os.system(f'echo {passw} | sudo -S cp {datas["project_path"]}save_conf/transport_yr.properties '
                  f'/opt/utm/transport/conf/transport.properties')
        print("Обрабатываю для юрика")
        file.write('yr')
        file.close()
    else:
        file.close()


def jacarta_user():
    os.system(f'echo {passw} | sudo -S supervisorctl stop utm')
    time.sleep(2)
    id = int(input("Выберите лицо:\n1)Физ.лицо\n2)Юр.лицо\n>>> "))

    os.system(f'mkdir {datas["project_path"]}save_conf')
    jacarta_chage(id)
    restarter()

def jacarta_istll():
    os.system(f'echo {passw} | sudo -S  ~/Загрузки/jacarta_UTM/install.sh')

def change_prop():
    old_path = datas['old_path']+datas['sp']+'.jar'

    # shutil.copy(old_path, datas['project_path'])
    os.system(f'echo {passw} | sudo -S  cp {old_path} {datas["project_path"]}')
    os.rename(f"{datas['sp']}.jar",f"{datas['sp']}.zip")
    # shutil.copy(old_path, datas['project_path'])
    os.system(f'echo {passw} | sudo -S  cp {old_path} {datas["project_path"]}')

    with ZipFile(f"{datas['sp']}.zip","r") as sp:
        sp.extract("sp/sp")
    shutil.copy(f'{datas["project_path"]}sp/sp', '/opt/encrypter/')
    # os.system(f'echo {passw} | sudo -S chmod +x -R /opt/encrypter/')

def deshifr():
    change_prop()
    varint = input("Выбор смены настроек\n1)Вручную\n2)Файлом\n>>> ")
    if varint == "1":
        os.system(
            'cd /opt/encrypter/ ; /opt/utm/jre/bin/java -cp /opt/encrypter/lib/"*" ru.centerinform.transport.conf.crypto.Encrypter ./sp')
        text = input("Введите запрос для изменения настроек (= заменяется на " "), exit: ")
        text = text.replace("=", " ")
        while text!="exit":
            os.system(f'cd /opt/encrypter/ ; /opt/utm/jre/bin/java -cp /opt/encrypter/lib/"*" ru.centerinform.transport.conf.crypto.Encrypter ./sp {text}')
            text = input("Введите запрос для изменения настроек (= заменяется на " "), exit: ")
            text = text.replace("="," ")
    elif varint == "2":
        with open("full sand", 'r') as props_list:
            props = props_list.readlines()
            print(props)
        for i in props:
            i=i.replace("="," ")
            i = i.replace("\n", "")
            try:
                os.system(
                    f'cd /opt/encrypter/ ; /opt/utm/jre/bin/java -cp '
                    f'/opt/encrypter/lib/"*" ru.centerinform.transport.conf.crypto.Encrypter ./sp {i}')
                print(f"Настройка изменена {i}")
            except:
                print(f"Ошибка {i}")
        print("\n\n")


    os.system('cd /opt/encrypter/ ; /opt/utm/jre/bin/java -cp /opt/encrypter/lib/"*" ru.centerinform.transport.conf.crypto.Encrypter ./sp')
    os.system(f'echo {passw} | sudo -S  chown -R ivan:root /home/ivan/PycharmProjects/utmmeet/UUUTM/')
    print(f"{datas['sp']}.zip"+" open as r.")
    with ZipFile(f"{datas['sp']}.zip", "r") as sp:
        sp.extract("META-INF/MANIFEST.MF")
        sp.extract("sp/spp")
    new_zip = ZipFile("sp-1.99.zip", "w")
    os.remove(f"{datas['project_path']}sp/sp")
    os.system(f'cp /opt/encrypter/sp {datas["project_path"]}sp/')
    new_zip.write("sp/sp")
    new_zip.write("sp/spp")
    new_zip.write("META-INF/MANIFEST.MF")
    new_zip.close()
    shutil.rmtree("sp")
    shutil.rmtree("META-INF")
    os.rename("sp-1.99.zip", "sp-1.99.jar")

def clear_buffer():
    os.system(f'echo {passw} | sudo -S rm {datas["project_path"]}backbones/{backbone_zip}')
    os.system(f'echo {passw} | sudo -S rm {datas["project_path"]}backbones/0{backbone_zip}')
    os.system(f'echo {passw} | sudo -S rm {datas["project_path"]}backbones/logback-spring.xml')
    os.system(f'echo {passw} | sudo -S rm {datas["project_path"]}backbones/logback-spring_copy.xml')

def debugg():
    os.system(f'echo {passw} | sudo -S supervisorctl stop utm')
    os.system(f'echo {passw} | sudo -S chown -R ivan:root /opt/')

    os.system(f'mkdir {datas["project_path"]}backbones')
    try:
        backbone = masking_backbone()
        print(backbone)
        backbone_zip = backbone + '.zip'
        backbone_jar = backbone + '.jar'
        os.system(f'echo {passw} | sudo -S cp /opt/utm/transport/lib/{backbone_jar} {datas["project_path"]}backbones/{backbone_zip}')
        os.system(f'echo {passw} | sudo -S chown -R ivan:root {datas["project_path"]}')

        print('Файл скопирован')
        with ZipFile(f'{datas["project_path"]}backbones/{backbone_zip}', 'r') as zip_ref:
            zip_ref.extract('logback-spring.xml',f'{datas["project_path"]}backbones/')

        print('файл распакован')
        print('меняю логирование')
        with open(f'{datas["project_path"]}backbones/logback-spring.xml','rt') as prop:
            with open(f'{datas["project_path"]}backbones/logback-spring_copy.xml','wt') as copy:
                    for line in prop:
                        if '<springProfile name="default,test,prod">' in line:
                            copy.write(line)
                            copy.write('        <logger name="ru.centerinform" level="DEBUG" />'+'\n')
                        else:
                            copy.write(line)
                    print('DEBUG логирование включено')
        print('изменения внесены')
        os.system(f'echo {passw} | sudo -S mv {datas["project_path"]}backbones/logback-spring_copy.xml {datas["project_path"]}backbones/logback-spring.xml')
        print('Арихивирую')

        with ZipFile(f'{datas["project_path"]}backbones/{backbone_zip}', 'r') as zip_ref:
            with ZipFile(f'backbones/0{backbone_zip}','a') as new_zip:
                for file in zip_ref.infolist():
                    buffer = zip_ref.read(file.filename)
                    if file.filename != 'logback-spring.xml':
                        new_zip.writestr(file,buffer)

        with ZipFile(f'backbones/0{backbone_zip}','a') as new_zip:
            new_zip.write('backbones/logback-spring.xml',arcname='logback-spring.xml')
        print('Файл был архивирован')
        print('Перенос в папку УТМ')
        os.system(f'echo {passw} | sudo -S chown -R ivan:root /opt/')
        os.system(f'echo {passw} | sudo -S rm /opt/utm/transport/lib/{backbone_jar}')
        os.system(f'echo {passw} | sudo -S mv {datas["project_path"]}backbones/0{backbone_zip} '
                  f'/opt/utm/transport/lib/{backbone_jar}')
        clear_buffer()
        print('Очистка буферной директории')
        os.system(f'echo {passw} | sudo -S supervisorctl start utm')




    except FileNotFoundError:
        print("Файл для параметров логирования не найден")
        backbone = None
    except:
        backbone = None
    finally:
        print(backbone)

def change_sp_settings():
    folders2 = {}
    d = datas['project_path']+'sp_ver/'
    folders = list(filter(lambda x: os.path.isdir(os.path.join(d, x)), os.listdir(d)))
    for id, value in enumerate(folders):
        folders2[id] = value
        print(id,value)
    choose = int(input(">>> "))
    if choose != None:
        choosed = folders2[choose]
    changed_path = d + choosed + '/*'
    file = open('save_conf/reinstal.txt', 'a')
    file.write('\nchanged '+changed_path)
    file.close()
    os.system(f'echo {passw} | sudo -S  chown -R ivan:root /opt/')
    os.system(f'echo {passw} | sudo -S  supervisorctl stop utm')
    os.system(f'echo {passw} | sudo -S  cp -i {changed_path} {datas["old_path"]}')
    os.system(f'echo {passw} | sudo -S  chown -R ivan:root /opt/')
    os.system(f'echo {passw} | sudo -S  supervisorctl start utm')
    print("\nШаблон установлен")
def new_properties():
    try:
        sp = masking_sp()
    except FileNotFoundError:
        print("Кажется вы забыли установить УТМ")
        return
    datas['sp'] = sp
    os.system(f'mkdir {datas["project_path"]}SaveProp')
    os.system(f'echo {passw} | sudo -S  cp /opt/utm/transport/lib/{datas["sp"]}.jar {datas["project_path"]}SaveProp')
    os.system(f'echo {passw} | sudo -S  cp {datas["project_path"]}sp-1.99.jar /opt/utm/transport/lib/')
    os.system(f'echo {passw} | sudo -S  chown -R ivan:root /opt/')
    # os.system(f'echo {passw} | sudo -S  mv -v /opt/utm/transport/lib/sp-1.99.jar /opt/utm/transport/lib/')
    os.system(f'echo {passw} | sudo -S supervisorctl restart utm')

# def old_prop():
#     global passw
#     os.system(f'echo {passw} | sudo -S rm /opt/utm/transport/lib/sp-1.40.jar')
#     os.system(f'echo {passw} | sudo -S cp {datas["project_path"]}SaveProp/sp-1.40.jar /opt/utm/transport/lib')
#     os.system(f'echo {passw} | sudo -S supervisorctl restart utm')

def clearDB():
    os.system(f'echo {passw} | sudo -S  supervisorctl stop utm')
    os.system(f'echo {passw} | sudo -S  chown -R ivan:root /opt/utm/')
    time.sleep(5)
    print("Рут")
    os.system(f'echo {passw} | sudo -S  rm -r /opt/utm/transport/transportDB')
    print("БД удалена")
    os.system(f'echo {passw} | sudo -S cp -i /opt/utm/transport/conf/transport.properties '
              f'~/ save_conf/transport_fill.properties')
    os.system(f'echo {passw} | sudo -S  chown -R ivan:root  ~/PycharmProjects/')
    file2 = open('save_conf/transport_fill2.properties', 'w')
    with open('save_conf/transport_fill.properties', 'r') as file:
        for line in file:
            with open('save_conf/last_prop.txt') as getter:
                liso = getter.readline()
                if 'fiz' in liso:
                    line = line.replace('crypto.lib.gost.keystorePassword=','crypto.lib.gost.keystorePassword=0987654321')
                    line = line.replace('crypto.lib.gost.keyPassword=', 'crypto.lib.gost.keyPassword=0987654321\ncrypto.lib.gost.serialNumber=')
                    line = line.replace('crypto.lib.pki.keystorePassword=', 'crypto.lib.pki.keystorePassword=11111111')
                    line = line.replace('crypto.lib.pki.keyPassword=', 'crypto.lib.pki.keyPassword=11111111')
                    line = line.replace('crypto.lib.gost.serialNumber=', 'crypto.lib.gost.serialNumber=1D9A90E46CA4E400005DB95381D0002')
                elif 'yr' in liso:
                    line = line.replace('crypto.lib.gost.keystorePassword=','crypto.lib.gost.keystorePassword=0987654321')
                    line = line.replace('crypto.lib.gost.keyPassword=', 'crypto.lib.gost.keyPassword=0987654321\ncrypto.lib.gost.serialNumber=')
                    line = line.replace('crypto.lib.pki.keystorePassword=', 'crypto.lib.pki.keystorePassword=11111111')
                    line = line.replace('crypto.lib.pki.keyPassword=', 'crypto.lib.pki.keyPassword=11111111')
                    line = line.replace('crypto.lib.gost.serialNumber=', 'crypto.lib.gost.serialNumber=1D9A90E44DF20100005DB94381D0002')
                else:
                    pass
            file2.writelines(f"{line}")
        print(liso)
    file2.close()

    print("Обрабатываю пароли")
    os.system(f'echo {passw} | sudo -S cp {datas["project_path"]}save_conf/transport_fill2.properties '
              f'/opt/utm/transport/conf/transport.properties')
    os.system(f'echo {passw} | sudo -S  supervisorctl start utm')

def restarter():
    os.system(f'echo {passw} | sudo -S supervisorctl restart utm')

def fast_reinstall():
    with open('save_conf/reinstal.txt','r') as file:
        flag = 0
        for line in file:
            if 'data' in line:
                line = line.replace('data ','')
                data_line = line
                flag+=1
            elif 'changed' in line:
                line = line.replace('changed ','')
                changed_line = line
                flag+=1


            if flag == 2:
                datas['sp'] = 'sp-1.99'
                clear_utm()
                time.sleep(5)
                print(data_line)
                os.system(f'echo {passw} | sudo -S  dpkg --install {data_line}')
                print('Переустановили УТМ')
                print(changed_line)
                os.system(f'echo {passw} | sudo -S  chown -R ivan:root /opt/')
                os.system(f'echo {passw} | sudo -S  supervisorctl stop utm')
                os.system(f'echo {passw} | sudo -S  cp -i {changed_line} {datas["old_path"]}')
                os.system(f'echo {passw} | sudo -S  chown -R ivan:root /opt/')
                os.system(f'echo {passw} | sudo -S  supervisorctl start utm')
                print("\nШаблон установлен")



update_settings()
data = input("\n1) Clear UTM\n2) Install UTM\n3) Change Properties\n4) UTM status\n5) Use changed propertiesn\n"
             "6) use template sp\n7) USER changer\n8) DELETE DB\n9) restart utm\n10) Debug\n11 reinstall\n(exit)\n")
while data != "exit":
    update_settings()
    if data == "1":
        clear_utm()
    elif data == "2":
        install_utm()
        sp = masking_sp()
    elif data == "3":
        try:
            sp = masking_sp()
        except FileNotFoundError:
            print("Кажется вы забыли установить УТМ")
            data = input(
                "\n1) Clear UTM\n2) Install UTM\n3) Change Properties\n4) UTM status\n5) Use changed propertiesn\n"
                "6) use template sp\n7) USER changer\n8) DELETE DB\n9) restart utm\n10) Debug\n11 reinstall\n(exit)\n")
            continue
        deshifr()
    elif data == "4":
        passw = input("Print password: ")
        os.system(f"echo {passw} | sudo -S supervisorctl status")
    elif data == "5":
        try:
            sp = masking_sp()
        except FileNotFoundError:
            print("Кажется вы забыли установить УТМ")
            data = input(
                "\n1) Clear UTM\n2) Install UTM\n3) Change Properties\n4) UTM status\n5) Use changed propertiesn\n"
                "6) use template sp\n7) USER changer\n8) DELETE DB\n9) restart utm\n10) Debug\n11 reinstall\n(exit)\n")
            continue
        if "sp-1.99.jar":
            new_properties()
            print("\nU here")
        else:
            print("U don`t have any document, named sp-1.99.jar")
    elif data == '6':
        change_sp_settings()
    elif data == "7":
        # print("Я плохая программа, не смогу отработать данную функцию, ожидаете патча")
        jacarta_user()
    elif data =="8":
        # print("Не рискуем, может сломать УТМ")
        # jacarta_istll()
        clearDB()
    elif data == "9":
        restarter()
    elif data == "10":
        start_backbone()
        debugg()
        clear_buffer()
    elif data == '11':
        fast_reinstall()
    update_settings()

    data = input("\n1) Clear UTM\n2) Install UTM\n3) Change Properties\n4) UTM status\n5) Use changed propertiesn\n"
                 "6) use template sp\n7) USER changer\n8) DELETE DB\n9) restart utm\n10) Debug\n11 reinstall\n(exit)\n")


