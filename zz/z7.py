import confluent_kafka as ck
import json
import random as ra
topics = ['some-topic']
srv = 'gitlab-ci.ru:9092' # кафка песка доступна снаружи
group = 'group-name'
conf = {'bootstrap.servers': srv,
                 'group.id': group,
       'enable.auto.commit': True,
        'auto.offset.reset': 'beginning'} #'earliest'}
consumer = ck.Consumer(conf)
consumer.subscribe(topics)

while True:
    msg = consumer.poll()
    if msg is None:
        break
    val = msg.value().decode('utf8')
    print(msg.offset(), val)

# НО
# для консума Н штук использовать метод consume()
# см https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-consumer

def keyhold(): # непременно интовый ключ, а не то приляжет барк
    t = 10000
    aint = ra.randint(t, t * t)
    return aint.to_bytes(4, byteorder='big')

mess ='{"type":"actwriteoff_v3", ' \
      '"uri":"030000412211-d5782d89-d551-4f82-800f-2ab9987b6930",' \
      ' "DocId":"WOF-0010203040", ' \
      '"date":"2021-09-03"}'
# непременно дата без времени, а не то приляжет сэйвер
proconf = {'bootstrap.servers': srv, 'client.id': 'urdu'}
producer = pro(proconf)
topic = 'Cheque'
msg = json.dumps(mess) # непременно явно сериализовать в json, а не то приляжет кх
producer.produce(topic, key=keyhold(), value=msg)
producer.flush()

# если надо запродюсить Н штук, то
for mes in somelist:
    producer.produce(topic, key=keyhold(), value=mes)
producer.flush() # т. е. комит пачки, а не по одному