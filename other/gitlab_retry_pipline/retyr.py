# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time
#
# link = "https://repo.r77.center-inform.ru/services/domestic/rsa/-/pipelines"
#
# try:
#     browser = webdriver.Chrome()
#     browser.get(link)
#
#     stage1 = browser.find_element(By.CSS_SELECTOR, "span[class='gl-display-inline-flex gl-align-items-center gl-border gl-z-index-1 ci-status-icon ci-status-icon-running js-ci-status-icon-running gl-rounded-full gl-justify-content-center gl-line-height-0 interactive borderless'] svg")
#     if stage1.aria_role
#
# finally:
#     # успеваем скопировать код за 30 секунд
#     time.sleep(5)
#     # закрываем браузер после всех манипуляций
#     browser.quit()
#
#
#

import time
from random import randint

from kafka import KafkaProducer
import json

path = input('KAFKA\n------------------\n\nWrite path file\n >>> ')

with open(path,'r') as doc_in:
    all_jsons = doc_in.readlines()
    k=1
    for i in all_jsons:
        new_i = i.replace('\n','')
        bootstrap_server = ['test-kafka1.fsrar.ru:9092', 'test-kafka2.fsrar.ru:9092', 'test-kafka3.fsrar.ru:9092']
        topic = 'new_mchd_reestr_in'
        message = json.loads(new_i)

        producer = KafkaProducer(
            bootstrap_servers=bootstrap_server,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        producer.send(topic, message)
        print(k,new_i,'Сообщение отправлено')
        producer.close()
        k+=1
        time.sleep(randint(1,12))