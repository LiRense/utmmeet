import time
from random import randint

from kafka import KafkaProducer
import json

path = input('KAFKA\n------------------\n\nWrite path file\n >>> ')

with open(path,'r') as doc_in:
    all_jsons = doc_in.readlines()
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
        print(new_i,'Сообщение отправлено')
        producer.close()
        time.sleep(randint(1,4))
