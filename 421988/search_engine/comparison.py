import json

import requests
import urllib3
import curlify


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_data_lk(inn, column_name, month):
    headers = {
        'accept': '*/*',
        'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJsYXN0TmFtZSI6IkF1dG8iLCJmaXJzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInJvbGVpZCI6IjAiLCJwZXJtaXNzaW9ucyI6IlJldGFpbCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.6_p87gJOz4GombT13glAKqk-iTYoTpkBIc9S3qT56TNJEAIZgK_QOZTTp1TTLZXoaZ6GrTgGUUWN9tglX8cqKQ',
    }
    params = {
        'year': '2023',
        'inn': inn,
    }
    response = requests.get('https://lk-test.egais.ru/lk-akciz/dashboard/akciz/', params=params, headers=headers,
                            verify=False)
    full_data = response.json()
    for i in full_data:
        if str(i['month']['periodMonth']) == str(month):
            if i['month']['declTaxBaseAnhydrousVolume'] == None:
                return 'null'
            else:
                return int(i['month']['declTaxBaseAnhydrousVolume'])


def get_data_old_lk():
    headers = {
        'accept': '*/*',
        'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJsYXN0TmFtZSI6IkF1dG8iLCJmaXJzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInJvbGVpZCI6IjAiLCJwZXJtaXNzaW9ucyI6IlJldGFpbCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.6_p87gJOz4GombT13glAKqk-iTYoTpkBIc9S3qT56TNJEAIZgK_QOZTTp1TTLZXoaZ6GrTgGUUWN9tglX8cqKQ',
    }
    data = {'sEcho': 3,
            'iColumns': 13,
            'sColumns': ',,,,,,,,,,,,',
            'iDisplayStart': 0,
            'iDisplayLength': 10,
            'mDataProp_0': 0,
            'sSearch_0': 9303019720,
            'bRegex_0': 'false',
            'bSearchable_0': 'true',
            'bSortable_0': 'true',
            'mDataProp_1': 1,
            'bRegex_1': 'false',
            'bSearchable_1': 'true',
            'bSortable_1': 'true',
            'mDataProp_2': 2,
            'bRegex_2':' false',
            'bSearchable_2': 'true',
            'bSortable_2': 'true',
            'mDataProp_3': 3,
            'bRegex_3': 'false',
            'bSearchable_3': 'true',
            'bSortable_3': 'true',
            'mDataProp_4': 4,
            'sSearch_4': '2023',
            'bRegex_4': 'false',
            'bSearchable_4': 'true',
            'bSortable_4': 'true',
            'mDataProp_5': 5,
            'bRegex_5': 'false',
            'bSearchable_5': 'true',
            'bSortable_5': 'true',
            'mDataProp_6': 6,
            'sSearch_6': '~',
            'bRegex_6': 'false',
            'bSearchable_6': 'true',
            'bSortable_6': 'true',
            'mDataProp_7': 7,
            'bRegex_7': 'false',
            'bSearchable_7': 'true',
            'bSortable_7': 'true',
            'mDataProp_8': 8,
            'bRegex_8': 'false',
            'bSearchable_8': 'true',
            'bSortable_8': 'true',
            'mDataProp_9': 9,
            'bRegex_9': 'false',
            'bSearchable_9': 'true',
            'bSortable_9': 'true',
            'mDataProp_10': 10,
            'bRegex_10': 'false',
            'bSearchable_10': 'true',
            'bSortable_10': 'true',
            'mDataProp_11': 11,
            'bRegex_11': 'false',
            'bSearchable_11': 'true',
            'bSortable_11': 'true',
            'mDataProp_12': 12,
            'bRegex_12': 'false',
            'bSearchable_12': 'false',
            'bSortable_12': 'false',
            'bRegex': 'false',
            'iSortCol_0': 6,
            'sSortDir_0': 'desc',
            'iSortingCols': 1,
            'sRangeSeparator': '~'}

    r = requests.post('https://lk.fsrar.ru/Goverment/ExciseDeclarations/GetDeclarationsList', json=data, headers=headers, verify=False)
    full_data = r.json()
    print(full_data)


inns = [9303019720,
        9402003103,
        3124010381,
        3128053185]

for inn in inns:
    print(f'INN {inn}\n________________________________')
    for month in range(1,13):
        from_lk = get_data_lk(inn, "declTaxBaseAnhydrousVolume", month)
        print(f'Месяц {month} - {from_lk}')
    print('________________________________')
