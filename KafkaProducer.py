import pandas as pd
from kafka import KafkaProducer
from time import sleep
from json import dumps
import json

producer = KafkaProducer(bootstrap_servers=['35.178.205.151:9092'],
                            value_serializer=lambda x: dumps(x).encode('utf-8'),
                            api_version=(2, 8, 0))

producer.flush()

df = pd.read_csv("Fire_SF.csv")

for index, row in df.iterrows():
    dict = df.sample(1).to_dict(orient="records")[0]
    producer.send('test_1', value=dict)
    print(index)
    print(dict)
    sleep(10)    # Apparently there has to be a delay since the cinsumer takes a while to send files to S3

print("Producer flushing in 60 seconds...")
sleep(30)
print("Producer flushing in 30 seconds...")
sleep(20)
print("Producer flushing in 10 seconds...")
sleep(10)
producer.flush()
print("Producer has been flushed.")