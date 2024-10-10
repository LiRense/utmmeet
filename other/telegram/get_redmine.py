import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import numpy as np
from numpy.distutils.conv_template import header
from pandas import DataFrame
import os.path

def log_in():
    # URL для страницы авторизации
    login_url = 'https://redmine.r77.center-inform.ru/login'
    # Создаем сессию
    with requests.Session() as session:
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        # Получаем страницу с формой авторизации
        response = session.get(login_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Извлекаем токен аутентификации из формы
        # Предположим, что токен находится в элементе <input> с атрибутом name="csrf_token"
        csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

        # print(f"CSRF Token: {csrf_token}")

        # Данные для авторизации
        payload = {
            'utf8': '%E2%9C%93',
            'username': 'i.martikhin',
            'password': 'Vfhnb[by_2401]',
            'authenticity_token': csrf_token,
            'login': '%D0%92%D1%85%D0%BE%D0%B4',
            'back_url': '%2F'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Отправляем POST-запрос для авторизации
        response = session.post(login_url, data=payload, headers=headers)

        # Проверяем, успешна ли авторизация
        if response.status_code == 200:
            # print("Авторизация успешна")

            # Теперь можно отправлять запросы к защищенным страницам
            protected_url = 'https://redmine.r77.center-inform.ru/issues?c%5B%5D=project&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=updated_on&c%5B%5D=start_date&c%5B%5D=created_on&c%5B%5D=due_date&f%5B%5D=status_id&f%5B%5D=assigned_to_id&f%5B%5D=project.status&op%5Bassigned_to_id%5D=%3D&op%5Bproject.status%5D=%3D&op%5Bstatus_id%5D=o&set_filter=1&sort=updated_on%3Adesc%2Ccreated_on%2Cproject&v%5Bassigned_to_id%5D%5B%5D=me&v%5Bproject.status%5D%5B%5D=1&v%5Bstatus_id%5D%5B%5D='
            protected_response = session.get(protected_url)
            # print(protected_response.text)
            soup = BeautifulSoup(protected_response.content, 'html.parser')
            table_class = 'list issues odd-even sort-by-updated-on sort-desc'  # Замените на класс вашей таблицы
            table = soup.find('table', class_=table_class)

            # Проверяем, что таблица найдена
            if table:
                table_html = str(table)

                # Используем StringIO для обработки строкового HTML-кода
                table_data = pd.read_html(StringIO(table_html))[0]
                table_data.pop('Unnamed: 0')
                table_data.pop('Unnamed: 11')
                table_data.pop('Трекер')
                table_data.pop('Статус')
                table_data.pop('Дата начала')
                table_data.pop('Создано')
                # print(table_data.keys())
                # Выводим массив
                return table_data
            else:
                return 2
        else:
            return 3

def converter(data:list):
    header=['#','Проект','Приоритет','Тема','Обновлено','Срок завершения']
    data.append(header)
    sp_sizes=[]
    for i in data:
        size_of_l1 = []
        for j in i:
            size_of_l1.append(len(str(j)))
        sp_sizes.append(size_of_l1)
    del data[-1]
    len_sp = len(sp_sizes[0])
    max_sizes = dict()
    for i in range(len_sp):
        max_num = 0
        for j in sp_sizes:
            if j[i] > max_num:
                max_num=j[i]
            else:
                pass
        max_sizes[i]=max_num
    # print(sp_sizes)
    # print(max_sizes)
    header_str = '|'
    for siz in max_sizes:
        header_str+=header[siz]+' '*(max_sizes[siz]-len(header[siz]))+'|'
    header_str+='\n|'
    for siz in max_sizes:
        header_str+='-'*(max_sizes[siz])+'|'
    for i in data:
        header_str += '\n|'
        for id, j in enumerate(i):
            header_str += str(j) + ' ' * (max_sizes[id] - len(str(j))) + '|'
    return header_str


def send(data_formated):
    file_path='last_data'
    if os.path.exists(file_path):
        file = open('last_data','r')
        lines_in_file = file.read()
        if lines_in_file != data_formated:
            message = '```\n' + data_formated + '\n```'
            token = "7026945021:AAGJPgkLXGsLF4emnvgtbLEIdcylQxQF3cQ"
            chat_id = '-1002242999028'
            params = {'chat_id': chat_id, 'text': message,'parse_mode': 'MarkdownV2'}
            response = requests.get('https://api.telegram.org/bot' + token + '/sendMessage', params=params)
            writed_file = open('last_data', 'w')
            writed_file.write(data_formated)
        else:
            pass
    else:
        writed_file = open('last_data','w')
        writed_file.write('')
        send(data_formated)

def save_jobs(text):
    with open('last_data','w') as saved:
        saved.write(text)



resurl = log_in()
if type(resurl) is DataFrame:
    new_res = resurl.values.tolist()
    # print(new_res)
    conv_res = converter(new_res)
    # print(conv_res)
    send(conv_res)
elif resurl==3:
    #"Авторизация не удалась"
    pass
elif resurl==2:
    #Нет таблицы -> пустая
    pass
