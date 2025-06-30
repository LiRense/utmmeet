from kafka import KafkaProducer
import json

num = int(input('1 - песок\n2 - тест\n3 - прод(не трогаем)\n>>> '))
if num == 1:
    bootstrap_server = 'gitlab-ci.ru:9092'
elif num == 2:
    bootstrap_server = ['test-kafka1.fsrar.ru:9092', 'test-kafka2.fsrar.ru:9092', 'test-kafka3.fsrar.ru:9092']

topic = input('Топик:\n>>> ')

with open('kafka_message','r') as message_full:
    raw_messages = message_full.readlines()
    for raw_message in raw_messages:
        message = json.loads(raw_message.replace('\n',''))
        print(f'Sended message >>>>    {message}')
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_server,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        producer.send(topic, message)
        print('Сообщение отправлено')
producer.close()
