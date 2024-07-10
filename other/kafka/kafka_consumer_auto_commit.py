import kafka
from kafka.consumer import KafkaConsumer
from kafka.producer import KafkaProducer
import json.decoder

consumer = KafkaConsumer(bootstrap_servers='test-kafka1.fsrar.ru:9092',
                         group_id='mchd-actualaizer-reestr-in',
                         consumer_timeout_ms=60000,
                         auto_offset_reset='earliest',
                         enable_auto_commit=True)

consumer.subscribe(['actualaizer_reestr_in'])

print("consumer is listening....")
try:
    for message in consumer:
        print(message.value.decode('utf-8'))

except KeyboardInterrupt:
    print("Aborted by user...")

finally:
    consumer.close()

    # import kafka
    # from kafka.consumer import KafkaConsumer
    # import json.decoder
    #
    # consumer = KafkaConsumer(bootstrap_servers='test-kafka1.fsrar.ru:9092',
    #                          group_id='mchd-actualaizer-reestr-in',
    #                          consumer_timeout_ms=60000,
    #                          auto_offset_reset='earliest',
    #                          enable_auto_commit=True)
    #
    # consumer.subscribe(['actualaizer_reestr_in'])
    # print("consumer is listening....")
    # try:
    #     for message in consumer:
    #         print(message.value.decode('utf-8'))
    #
    # except KeyboardInterrupt:
    #     print("Aborted by user...")
    #
    # finally:
    #     consumer.close()


# produser = KafkaProducer(bootstrap_servers='test-kafka1.fsrar.ru:9092',
#                          client_id='Ivan-script',
#                          )
# message = ''
#
# produser.send(topic='topic-name',value=message)