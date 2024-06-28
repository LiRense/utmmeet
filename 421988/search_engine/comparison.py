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
            if i['month'][column_name] == None:
                return 'null'
            else:
                return int(i['month'][column_name])


def get_data_old_lk():
    headers = {
        'accept': '*/*',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiZGV2ZWxvcGVyIiwiZmlyc3ROYW1lIjoiUGV0ZXIgUGV0cm92aWNoIiwibGFzdE5hbWUiOiJQZXRyb3YiLCJsb2NhbGl0eSI6ItCc0L7RgdC60LLQsCIsInJlZ2lvbiI6Ijc3IiwicmVnaW9uQ29kZSI6Ijc3IiwidXNlcmlkIjoiMzgzIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZWlkZW50aWZpZXIiOiIzODMiLCJyb2xlaWQiOiIxMiIsInBlcm1pc3Npb25zIjoiVXNlcnMsUm9sZXMsTmV3cyxTdGF0aXN0aWNhbEluZixDb25zdW1wdGlvbixSZXRhaWwsTWFya2V0UGFydGljaXBhbnRzLE1hcmtldFBhcnRpY2lwYW50c1YyLFJlcG9ydHMsT3JnYW5pemF0aW9ucyxSZXBvcnRUZW1wbGF0ZXMsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxTdGF0aXN0aWNhbEluZixTdGF0aXN0aWNhbEluZixSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsU3RhdGlzdGljYWxJbmYiLCJsaXN0UmVnaW9uQ29kZXMiOiI3NyIsImV4cCI6MTcxNTAwMDcyOSwiaXNzIjoiQ0FFZ2FpcyIsImF1ZCI6IlVzZXJzIn0.U6Z5t6Epd-QGZWScEVNZFVmvX_ZsSQzXxossV7F4hj8',
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

columns = ['declTaxBaseVolume',
           'declTaxBaseAnhydrousVolume',
           'declSumForTaxDeductGrape',
           'declSumTaxDeductNonGrape',
           'declSumOnGrape']

# inns = [3128053185,
#         9303019720,
#         9402003103,
#         3124010381,
#         3128053185]

with open('inn.txt','r') as innns:
    inns = innns.readlines()


for column in columns:
    pass
file_new_lk = open('new_lk','w')
for inn in inns:
    file_new_lk.write(f'INN {int(inn)}\n________________________________\n')
    print(f'INN {inn}\n________________________________')
    for month in range(1,13):
        from_lk = get_data_lk(int(inn), 'declTaxBaseVolume', month)
        file_new_lk.write(f'Месяц {month} - {from_lk}\n')
        print(f'Месяц {month} - {from_lk}')
    file_new_lk.write('________________________________\n')
    print('________________________________')
