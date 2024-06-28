from kafka import KafkaProducer
import json

num = int(input('1 - песок\n2 - тест\n3 - прод(не трогаем)\n>>> '))
if num == 1:
    bootstrap_server = 'gitlab-ci.ru:9092'
elif num == 2:
    bootstrap_server = ['test-kafka1.fsrar.ru:9092', 'test-kafka2.fsrar.ru:9092', 'test-kafka3.fsrar.ru:9092']

topic = input('Топик:\n>>> ')

message = json.loads(input('Сообщение для отправки:\n>>> '))

# message_json = json.dumps(message, ensure_ascii=False)

producer = KafkaProducer(
    bootstrap_servers=bootstrap_server,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send(topic, message)

print('Сообщение отправдено')
producer.close()