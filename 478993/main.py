from DataBase.connection import *

file_w = open('result.txt', 'w')
with open('fsrars.txt','r') as fsrars:
    fsrars_list = fsrars.readlines()
    print(fsrars_list)
    for i in fsrars_list:
        fsrar = i.replace('\n','')

        sql_request = f'''
        select fsrar_id, mchd_reestr_id, is_active from mchd_reestr_keys mrk 
        where fsrar_id = '{fsrar}'
        order by date_inserted desc 
        limit 1
        '''

        connection_db = Connecting()
        tunnel = connection_db.tooneling(jump_host='10.0.50.208', jump_port=20010, remote_host='10.10.5.189', remote_port=5432, username='martikhin',
                                         ssh_pkey='/home/ivan/.ssh/id_rsa')

        result = connection_db.pg_sql(tunnel,'mchd','mchd_service','Qwerty1234',sql_request)
        fsrar = result[0][0]
        mchd_id = result[0][1]
        rsa_active = result[0][2]

        if rsa_active == True:
            sql_request2 = f'''
            select mchd_number, is_active from mchd_reestr
            where id = '{mchd_id}'
            '''
            result_2 = connection_db.pg_sql(tunnel,'mchd','mchd_service','Qwerty1234',sql_request2)

            mchd_number = result_2[0][0]
            mchd_active = result_2[0][1]
            if mchd_active == False:
                file_w.write(f'{fsrar}  ||  РСА ключ активен || МЧД {mchd_number} статус {mchd_active} --- ОТБИВАЕМ ЛЕГИТИМНО\n')
                print(f'{fsrar}  ||  РСА ключ активен || МЧД {mchd_number} статус {mchd_active} --- ОТБИВАЕМ ЛЕГИТИМНО')
            else:
                # result3 = connection_db.pg_sql(tunnel, 'mchd', 'mchd_service', 'Qwerty1234', 'select * from ')
                file_w.write(f'{fsrar}  ||  РСА ключ активен || МЧД {mchd_number} статус {mchd_active} --- ОТБИВАЕМ НЕЛЕГИТИМНО\n')
                print(f'{fsrar}  ||  РСА ключ активен || МЧД {mchd_number} статус {mchd_active} --- ОТБИВАЕМ НЕЛЕГИТИМНО')
        elif rsa_active == False:
            file_w.write(f'{fsrar}  ||  РСА ключ неактивен --- ОТБИВАЕМ ЛЕГИТИМНО\n')
            print(f'{fsrar}  ||  РСА ключ неактивен --- ОТБИВАЕМ ЛЕГИТИМНО')
        else:
            file_w.write(f'{fsrar}  ||  РСА ключей не найдено --- ОТБИВАЕМ ЛЕГИТИМНО\n')
            print(f'{fsrar}  ||  РСА ключей не найдено --- ОТБИВАЕМ ЛЕГИТИМНО')