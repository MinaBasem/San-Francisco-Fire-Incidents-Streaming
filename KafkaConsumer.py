# Consumer code as a single file

import os
import boto3
import json
import csv
import glob
from time import sleep
from json import dumps,loads
from s3fs import S3FileSystem
from datetime import datetime
from kafka import KafkaConsumer

s3 = boto3.resource('s3')
access_point_arn = "arn:aws:s3:eu-west-2:116685337455:accesspoint/test-access-point"

consumer = KafkaConsumer('test_1',
     bootstrap_servers=['35.178.205.151:9092'], #add your IP here
    value_deserializer=lambda x: loads(x.decode('utf-8')),
    api_version=(2, 8, 0))

#create an empty csv file and add 2 rows to it
with open('full_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['key', 'value'])

# for count, i in enumerate(consumer):
#     now = datetime.now()
#     now = now.strftime("%Y-%m-%d.%H:%M:%S")
#     filename = "data_{}_{}.json".format(count, now)
#     print(count)
#     print(i.value)
#     with open("temp_data/{}.json".format(filename), 'w') as file:
#         json.dump(i.value, file)
#         s3.Bucket(access_point_arn).upload_file("temp_data/{}.json".format(filename), "fire-sf-project" "/data/{}.json".format(filename))
#         print(" --- successfully uploaded")
#         #os.remove("temp_data/{}.json".format(filename))

# objective: collect all json rows and send them to a single file

now = datetime.now()
now = now.strftime("%Y-%m-%d.%H:%M:%S")

for count, i in enumerate(consumer):
    print(count)
    print(i.value)
    with open("temp_data/full_data_{}.json".format(now), 'a') as file:
        json.dump(i.value, file)
    s3.Bucket(access_point_arn).upload_file("temp_data/full_data_{}.json".format(now), "fire-sf-project" "/data/full_data_{}.json".format(now))
    print(" --- successfully uploaded")