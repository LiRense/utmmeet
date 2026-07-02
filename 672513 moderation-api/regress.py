import csv
import pandas as pd
from itertools import product
import configparser
import requests
import json
from typing import Optional, Dict, Any, Union
from loguru import logger
import psycopg2


class CSV_getter():

    def __init__(self, filename='test_cases.csv'):
        self.filename = filename
        self.df = None

    def config_pars(self):
        config = configparser.ConfigParser(interpolation=None)
        config.read('config.ini')

        result = {
            'swagger_url': config.get('Swagger address', 'url', fallback='http://localhost'),
            'method': config.get('Token path', 'method', fallback='POST'),
            'endpoint': config.get('Token path', 'endpoint', fallback='/token'),
            'token_url': config.get('Token path', 'token_url', fallback='/token'),
            'certificate': config.getboolean('Token path', 'certificate', fallback=False),
            'basic_auth': config.get('Token path', 'basic_auth',
                                     fallback='Basic cmVzZXQtbW9uaXRvcmluZy1yZXN1bHRzOmZhbHNl')
        }

        for section in config.sections():
            if section.startswith('DB_'):
                var_name = section.lower()
                result[var_name] = dict(config.items(section))

        return result

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
                if 'request' in row:
                    test['request'] = row['request']

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
                  timeout: int = 30,
                  verify: Optional[bool] = None):
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
            files: Файлы для multipart/form-data
            timeout: Таймаут запроса в секундах
        Returns:
            Response объект от requests
        """
        if verify is None:
            verify = self.config_pars()['certificate']

        full_url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        request_headers = headers.copy() if headers else {}
        request_params = params or {}
        request_data = None

        logger.debug('Checking ...')

        if files:
            for key, value in files.items():
                if value == ('', ''):
                    logger.debug(f"Обнаружен пустой файл: {key} -> будет как -F '{key}='")

        if bearer:
            if 'Bearer' in bearer or 'Basic' in bearer:
                request_headers['Authorization'] = bearer
            else:
                request_headers['Authorization'] = f'Bearer {bearer}'

        if files:
            # Если есть файлы - requests сам установит multipart/form-data
            logger.debug("Запрос с файлами - Content-Type будет установлен автоматически")
            # Не трогаем Content-Type вообще
        elif data and 'Content-Type' not in request_headers:
            # Только для запросов БЕЗ файлов устанавливаем application/json
            request_headers['Content-Type'] = 'application/json'
            logger.debug("Установлен Content-Type: application/json")

        if data:
            if isinstance(data, dict) and request_headers.get('Content-Type') == 'application/json':
                request_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            elif isinstance(data, str):
                request_data = data.encode('utf-8')
            elif isinstance(data, (list, tuple)):
                request_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            else:
                request_data = data

        try:
            logger.debug('request sending')
            logger.debug(f"URL: {full_url}")
            logger.debug(f"Method: {method}")
            logger.debug(f"Headers: {request_headers}")
            logger.debug(f"Has files: {files is not None}")
            if files:
                logger.debug(f"Files keys: {list(files.keys())}")

            response = requests.request(
                method=method.upper(),
                url=full_url,
                params=request_params,
                headers=request_headers,
                data=request_data,
                files=files,
                timeout=timeout,
                verify=verify
            )
            logger.debug('response got')

            return True, response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return False, e

        def get_bearer(self):
            bearer_path = self.config_pars()
            result, response = self.send_curl(base_url=bearer_path['token_url'],
                                              endpoint=bearer_path['endpoint'],
                                              method=bearer_path['method'])
            try:
                status = response.status_code
                res_text = response.text
                return [status, res_text]
            except Exception as e:
                return e


class DB_placer():
    def __init__(self, db, user, password, host, port, sql_req=''):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.sql_req = sql_req

    def inserter(self):
        logger.debug('Выполняю insert')

        conn = None
        try:
            # Подключаемся к БД
            conn = psycopg2.connect(
                dbname=self.db,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )

            logger.debug('Подключение к Postgre успешно')
            # Создаем курсор
            cursor = conn.cursor()

            logger.debug('Запрос выполняется')

            if isinstance(self.sql_req, tuple) and len(self.sql_req) == 2:
                query, params = self.sql_req
                cursor.execute(query, params)
            else:
                query = self.sql_req
                cursor.execute(query)

            if isinstance(query, str) and query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                conn.commit()
                return result
            else:
                conn.commit()
                return None

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Ошибка при работе с PostgreSQL: {error}")
            if conn:
                conn.rollback()
            return None
        finally:
            # Закрываем соединение
            if conn is not None:
                conn.close()
                logger.debug("Соединение с PostgreSQL закрыто")


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

