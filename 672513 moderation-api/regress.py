import csv
import pandas as pd
from itertools import product
import configparser
import requests
import json
from typing import Optional, Dict, Any, Union
from loguru import logger


class CSV_getter():

    def __init__(self, filename='test_cases.csv'):
        self.filename = filename
        self.df = None

    def config_pars(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        return {
            'swagger_url': config.get('Swagger address', 'url', fallback='http://localhost'),
            'method': config.get('Token path', 'method', fallback='POST'),
            'endpoint': config.get('Token path', 'endpoint', fallback='/token')
        }

    def get_rows(self):
        """Читает CSV файл и возвращает только активные строки (isActive = TRUE)"""
        self.df = pd.read_csv(self.filename)

        # Фильтруем только активные строки
        if 'isActive' in self.df.columns:
            # Приводим к булевому типу (учитываем разные варианты записи TRUE)
            self.df = self.df[self.df['isActive'].astype(str).str.upper() == 'TRUE']

        return self.df

    def get_active_endpoints(self):
        """Возвращает список уникальных endpoint'ов у активных записей"""
        if self.df is None:
            self.get_rows()

        if 'endpoint' in self.df.columns:
            return self.df['endpoint'].unique().tolist()
        return []

    def get_grouped_by_endpoint(self):
        """Возвращает словарь с группами по endpoint только для активных записей"""
        if self.df is None:
            self.get_rows()

        # Возвращаем словарь {endpoint_name: group_df}
        grouped_dict = {}
        if 'endpoint' in self.df.columns:
            for endpoint_name, group in self.df.groupby('endpoint'):
                grouped_dict[endpoint_name] = group

        return grouped_dict

    def get_endpoint_groups(self):
        """Возвращает итератор по группам endpoint только для активных записей"""
        if self.df is None:
            self.get_rows()

        if 'endpoint' in self.df.columns:
            return self.df.groupby('endpoint')
        return None

    def get_rows_by_endpoint(self, endpoint_name):
        """Возвращает все активные строки для конкретного endpoint"""
        if self.df is None:
            self.get_rows()

        if 'endpoint' in self.df.columns:
            return self.df[self.df['endpoint'] == endpoint_name]
        return pd.DataFrame()

    def generate_tests_for_group(self, group):
        """Генерирует все тесты для группы строк одного эндпоинта"""
        all_tests = []

        for id, row in group.iterrows():
            tests = self.make_tests(id, row)
            # Добавляем метаданные из исходной строки
            for test in tests:
                test['method'] = row['method']
                test['content-type'] = row['content-type']
                test['expCode'] = row['expCode']
                test['auth_code_err'] = row['auth_code_err']
                # Добавляем информацию об активности (может быть полезна)
                if 'isActive' in row:
                    test['isActive'] = row['isActive']
            all_tests.extend(tests)

        return all_tests

    def params_test(self, id, row):
        min_params = row['min_params']
        max_params = row['parameters']

        variation = []

        if pd.notna(max_params) and (max_params == min_params):
            copy_row = row.copy()
            copy_row['min_params'] = ''
            variation.append(copy_row)
        elif pd.notna(max_params) and (max_params != min_params):
            copy_row = row.copy()
            copy_row['min_params'] = ''
            variation.append(copy_row)

            copy_row_2 = row.copy()
            copy_row_2['parameters'] = ''
            variation.append(copy_row_2)
        else:
            variation.append(row)

        return id, variation

    def body_test(self, id, row):
        min_body = row['min_req_body']
        max_body = row['request_body']

        variation = []

        if pd.notna(max_body) and (max_body == min_body):
            copy_row = row.copy()
            copy_row['min_req_body'] = ''
            variation.append(copy_row)
        elif pd.notna(max_body) and (max_body != min_body):
            copy_row = row.copy()
            copy_row['min_req_body'] = ''
            variation.append(copy_row)

            copy_row_2 = row.copy()
            copy_row_2['request_body'] = ''
            variation.append(copy_row_2)
        else:
            variation.append(row)

        return id, variation

    def files_test(self, id, row):
        files_min = row['files_min']
        files_max = row['files_max']

        variation = []

        if pd.notna(files_max) and (files_max == files_min):
            copy_row = row.copy()
            copy_row['files_min'] = ''
            variation.append(copy_row)
        elif pd.notna(files_max) and (files_max != files_min):
            copy_row = row.copy()
            copy_row['files_min'] = ''
            variation.append(copy_row)

            copy_row_2 = row.copy()
            copy_row_2['files_max'] = ''
            variation.append(copy_row_2)
        else:
            variation.append(row)

        return id, variation

    def make_tests(self, id, row):
        # Получаем вариации для каждого измерения
        req_id, req_var = self.params_test(id, row)
        body_id, body_var = self.body_test(id, row)
        files_id, files_var = self.files_test(id, row)

        all_combinations = []

        # Комбинируем все три измерения
        for req in req_var:
            for body in body_var:
                for files in files_var:
                    # Создаём копию req
                    combined = req.copy()

                    # ОЧИЩАЕМ поля тела (как в вашем старом коде)
                    combined['min_req_body'] = ''
                    combined['request_body'] = ''

                    # ОЧИЩАЕМ поля файлов
                    combined['files_min'] = ''
                    combined['files_max'] = ''

                    # Заполняем поля тела из body вариации
                    combined['min_req_body'] = body['min_req_body']
                    combined['request_body'] = body['request_body']

                    # Заполняем поля файлов из files вариации
                    combined['files_min'] = files['files_min']
                    combined['files_max'] = files['files_max']

                    all_combinations.append(combined)

        return all_combinations


    def send_curl(self,
                  base_url: str = None,
                  endpoint: str = None,
                  params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None,
                  bearer: Optional[str] = None,
                  method: str = 'GET',
                  data: Optional[Union[Dict, str]] = None,
                  files: Optional[Dict[str, Any]] = None,
                  timeout: int = 30):

        """
           curl

           Args:
               base_url:  'https://api.example.com'
               endpoint: '/users'
               params: Параметры запроса (query parameters)
               headers: Дополнительные заголовки
               bearer: Bearer токен для авторизации (если None - без авторизации)
               method: HTTP метод ('GET', 'POST', 'PUT', 'DELETE', и т.д.)
               data: Данные для отправки в теле запроса
               timeout: Таймаут запроса в секундах

           Returns:
               Response объект от requests
           """

        full_url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        request_headers = headers.copy() if headers else {}
        request_params = params or {}
        request_data = None

        logger.debug('Checking ...')


        if bearer:
            request_headers['Authorization'] = f'{bearer}' if 'Bearer' in bearer else f'Bearer {bearer}'
        if data and 'Content-Type' not in request_headers:
            request_headers['Content-Type'] = 'application/json'
        if data:
            if isinstance(data, dict) and request_headers.get('Content-Type') == 'application/json':
                request_data = json.dumps(data)
            else:
                request_data = data

        try:
            logger.debug('request sending')

            response = requests.request(
                method=method.upper(),
                url=full_url,
                params=request_params,
                headers=request_headers,
                data=request_data,
                files=files,
                timeout=timeout
            )
            logger.debug('response got')

            # response.raise_for_status()
            return True, response

        except requests.exceptions.RequestException as e:
            return False, e


    def get_bearer(self):
        bearer_path = self.config_pars()
        result, response = self.send_curl(base_url=bearer_path['swagger_url'],
                       endpoint=bearer_path['endpoint'],
                       method=bearer_path['method'])
        try:
            status = response.status_code
            res_text = response.text
            return [status, res_text]
        except Exception as e:
            return e


# cccsv = CSV_getter('test_cases.csv')
# df = cccsv.get_rows()
# for id, row in df.iterrows():
#     if id == 0:
#         print(cccsv.make_tests(id, row)[0])
#
# print(cccsv.config_pars())
#
# cccsv.get_bearer()












"""
response = send_curl_request(
    base_url='https://jsonplaceholder.typicode.com',
    endpoint='posts',
    params={'userId': 1}
)
print(response.json())

# 2. GET запрос с Bearer авторизацией
response = send_curl_request(
    base_url='https://api.example.com',
    endpoint='users/profile',
    bearer='your_token_here',
    headers={'Accept': 'application/json'}
)

# 3. POST запрос с данными
response = send_curl_request(
    base_url='https://api.example.com',
    endpoint='posts',
    method='POST',
    bearer='your_token_here',
    data={'title': 'New Post', 'content': 'Hello World'},
    headers={'Custom-Header': 'custom_value'}
)

# 4. Запрос с параметрами в URL
response = send_curl_request(
    base_url='https://api.example.com',
    endpoint='search',
    params={'q': 'python', 'page': 1, 'limit': 10}
)

# 5. Удобная функция для быстрого вызова
def quick_get(url: str, bearer: Optional[str] = None):
    #Быстрый GET запрос
    return send_curl_request(
        base_url=url.split('/')[0] + '//' + url.split('/')[2],
        endpoint='/'.join(url.split('/')[3:]),
        bearer=bearer
    )
"""

