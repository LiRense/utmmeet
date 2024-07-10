import os

import kafka
from kafka.consumer import KafkaConsumer
import json.decoder

where= 'martikhin@DockerHub:'
place = "/home/ldapusers/martikhin"
full = where+place

os.system(f"scp /home/ivan/PycharmProjects/utmmeet/other/kafka_consumer_auto_commit.py {full}")
os.system('ssh martikhin@DockerHub python3 kafka_consumer_auto_commit.py')