import pickle

import requests
import urllib3
import curlify


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
file = open('akciz_resultat2','w')
# districts = 'curl -X GET "https://lk-test.egais.ru/lk-akciz/dashboard/akciz/getFederalDistrictSpr" -H  "accept: */*" -H  "Authorization: Bearer eyJhbGciOiJIUzUxMiJ9.eyJsYXN0TmFtZSI6IkF1dG8iLCJmaXJzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInJvbGVpZCI6IjAiLCJwZXJtaXNzaW9ucyI6IlJldGFpbCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.6_p87gJOz4GombT13glAKqk-iTYoTpkBIc9S3qT56TNJEAIZgK_QOZTTp1TTLZXoaZ6GrTgGUUWN9tglX8cqKQ"'
# regions = 'curl -X GET "https://lk-test.egais.ru/lk-akciz/dashboard/akciz/getRegionSpr?id=1" -H  "accept: */*" -H  "Authorization: Bearer eyJhbGciOiJIUzUxMiJ9.eyJsYXN0TmFtZSI6IkF1dG8iLCJmaXJzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInJvbGVpZCI6IjAiLCJwZXJtaXNzaW9ucyI6IlJldGFpbCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.6_p87gJOz4GombT13glAKqk-iTYoTpkBIc9S3qT56TNJEAIZgK_QOZTTp1TTLZXoaZ6GrTgGUUWN9tglX8cqKQ"'

headers = {
    'accept': '*/*',
    'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJsYXN0TmFtZSI6IkF1dG8iLCJmaXJzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInJvbGVpZCI6IjAiLCJwZXJtaXNzaW9ucyI6IlJldGFpbCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.6_p87gJOz4GombT13glAKqk-iTYoTpkBIc9S3qT56TNJEAIZgK_QOZTTp1TTLZXoaZ6GrTgGUUWN9tglX8cqKQ',
}

distr_response = requests.get(
    'https://lk-test.egais.ru/lk-akciz/dashboard/akciz/getFederalDistrictSpr',
    headers=headers,
    verify=False,
)
distr_data = distr_response.json()
file.write(f'{distr_data}\n')
file.write('_________________________________________________\n')
print(distr_data)
print('_________________________________________________\n')

for i in distr_data:
    file.write(f'Округ {i} \n')
    print('Округ',i,'\n')
    regions = []
    for j in range(1,100):
        if len(str(j)) == 1:
            j = '0'+str(j)

        region_params = {
            'id': str(j),
        }
        region_response = requests.get(
            'https://lk-test.egais.ru/lk-akciz/dashboard/akciz/getRegionSpr',
            params=region_params,
            headers=headers,
            verify=False,
        )
        region_data = region_response.json()
        # print(j)
        if region_data != []:
            if region_data[0]['districtSprResponse'] == i:
                regions.append(region_data[0])
    for s in regions:
        file.write(f'Регион: {s["codeFns"]} {s["name"]}\n')
        print('Регион: ',s['codeFns'],s['name'])
        couner_fails = []
        params = {
            'year': '2023',
            'district': i['id'],
            'region': s['codeFns'],
        }

        response = requests.get('https://lk-test.egais.ru/lk-akciz/dashboard/akciz/', params=params, headers=headers,
                                verify=False)

        full_data = response.json()
        if full_data != []:
            for kl in full_data:
                sum = 0
                file.write(f'month: {kl["month"]["periodMonth"]} - budget {kl["month"]["egaisSumPayToBudget"]}\n')
                print('month:',kl['month']['periodMonth'],'- budget',kl['month']['egaisSumPayToBudget'])
                if kl['month']['egaisSumPayToBudget'] != 0:
                    month_reg = kl["month"]["periodMonth"]
                    params = {
                        'page':'0',
                        'size':9999,
                        'filter': f'[["year","=",2023],"and",["month","=",{month_reg}]]',
                        'federalDistrictList': i['id'],
                        'subjectRfList': s['codeFns']
                    }

                    response = requests.get('https://lk-test.egais.ru/lk-akciz/dashboard/akciz/getTaxExciseShipmentWithPagination/', params=params,
                                            headers=headers,
                                            verify=False)
                    data = response.json()
                    # print(curlify.to_curl(response.request))
                    # print(data)
                    for con in data['content']:
                        sum += con['exciseSum']
                    file.write(f'Получили {sum}, {round(sum) == kl["month"]["egaisSumPayToBudget"]}\n')
                    print('Получили',sum, round(sum) == kl['month']['egaisSumPayToBudget'])
                    if round(sum) != kl['month']['egaisSumPayToBudget']:
                        couner_fails.append({'month':month_reg,'Главная':kl['month']['egaisSumPayToBudget'], 'Дочерняя':sum,'Разница':abs(kl['month']['egaisSumPayToBudget']-sum)})
            print('_________________________________________________\n')
            file.write('_________________________________________________\n')
        else:
            file.write('Пустой ответ\n_________________________________________________\n')
            print('Пустой ответ\n_________________________________________________\n')
        file.write(f'В регионе  {s["codeFns"]} {s["name"]},  содержится ошибок: {len(couner_fails)}\n')
        print('В регионе', s['codeFns'], s['name'], 'содержится ошибок:', len(couner_fails))
        if len(couner_fails) != 0:
            for hel in couner_fails:
                file.write(f"{hel}\n")

            print(couner_fails)
        file.write('====================================================\n')
        print('\n====================================================\n')

file.close()

