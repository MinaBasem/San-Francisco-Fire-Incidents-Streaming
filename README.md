<div align="center">
  <H1 style="font-size: 100;">:fire_engine::fire: San Francisco Fire Incidents Streaming Pipeline :fire::fire_engine:</H1>
  <img src="https://github.com/MinaBasem/San-Francisco-Fires-Pipeline/assets/42482261/36476332-f39b-4dba-a461-cc9be7201cfc" alt="Architecture Diagram">
</div>

## Overview
<img align="right" width="480" height="220" src="https://github.com/MinaBasem/San-Francisco-Fires-Pipeline/assets/42482261/a22e93f0-5fe6-46a8-a45f-72c7cebb33f5.jpg">
This project is aimed at learning Kafka, its uses and when it should be used.


Data is obtained through a JSON endpoint and sent downstream to an EC2 instance hosting Kafka, where a topic is created, along with a listener.
The whole process is orchestrated through an Airflow DAG that runs the import script then both the Producer and Consumer scripts simultaneously.

The producer script creates a file that holds all streamed data which is then sent to an S3 bucket.

Glue Crawler collects all that data into a table where it can be later on queried through Athena.

Finally the collected data is stored in an RDS instance.

## About the Dataset

```
Columns: 64
Rows: ~647,000 (As of December, 2023)
Created: December 19, 2015
```

The dataset used in this project is from [DataSF - Fire Incidents](https://data.sfgov.org/Public-Safety/Fire-Incidents/wr8u-xric/about_data), which is updated on a daily basis where fire incidents throughout San Fransisco are recorded.

Fire Incidents includes a summary of each (non-medical) incident to which the SF Fire Department responded. Each incident record includes the call number, incident number, address, number and type of each unit responding, call type, prime situation (field observation), actions taken, and property loss.

The JSON endpoint returns only the first 1000 rows when unfiltered (unqueried)
In order to return the latest 10 rows, the following link was used instead:
```
https://data.sfgov.org/resource/wr8u-xric.csv?$order=incident_date DESC&$limit=10
```

## Setting up the EC2 instance and Kafka

<img align="right" width="185" height="200" src="https://github.com/MinaBasem/San-Francisco-Fires-Pipeline/assets/42482261/79a0fea4-2813-46d0-864a-8bb558711fa6" alt="Architecture Diagram">
The Kafka server can be hosted either locally or on cloud.
In this project an EC2 instance was used.
The steps to set up the EC2 instance are as follows:

1. Start an EC2 instance (preferrably a t2.micro since this is a small project)
2. Launch the instance
3. Install Java JDK and Kafka and set them up
4. Configure the IP in `config/server.properties` file by adding the EC2 instance Public IPv4
5. Start Zookeeper `bin/zookeeper-server-start.sh config/zookeeper.properties`
6. Start Kafka Server `bin/kafka-server-start.sh config/server.properties`

The Kafka setup should be complete.

Topic creation (test_1 in this case), producer, and consumer are next:
```
bin/kafka-topics.sh --create --topic test_1 --bootstrap-server 35.178.205.151:9092 --replication-factor 1 --partitions 1
bin/kafka-console-producer.sh --topic test_1 --bootstrap-server 35.178.205.151:9092
bin/kafka-console-consumer.sh --topic test_1 --bootstrap-server 35.178.205.151:9092 (In a new terminal)
```

## import_fire_data.py

Obtains data from the JSON endpoint as JSON, converts it to CSV and saved into a local file `Fire_SF.csv'.
The obtained data has a total of 64 columns, in this script they are narrowed down to 28 columns, leaving only the more relevant data in hand.

## KafkaProducer.py

Flushes any data stored beforehand.
Starts the Kafka Producer session and serializes data to `utf-8` (note that for some users, an api_version has to be specified).
The script then streams data from the `Fire_SF.csv` file while converting each row to a JSON record.
Finally, the script flushes all congested data after 60 seconds of sending the last record.
Note: The KafkaProcuder.py and KafkaProducer.py are run simultaneously through the DAG so stream is made in real time.

## KafkaConsumer.py

Creates a connection to the S3 bucket, in this case an S3 access point was used to connect to the S3 bucket.
Consumer session is started and starts retreiving the streamed data.
Creates a file JSON file named `full_data_date.time.json` where all streamed data is appended and uploaded to the bucket.
A sample of the data sent to the bucket can be found below.

![Screen Shot 2023-12-09 at 2 25 44 PM](https://github.com/MinaBasem/San-Francisco-Fires-Pipeline/assets/42482261/fb0a62ad-3283-4233-ac0d-c92e5c31a2e1)

## airflow_scheduling.py

Orchestrates the entire process and runs the DAG once a day
Runs the `import_fire_data.csv` file, when finished, procceeds to run `KafkaProducer.py` and `KafkaConsumer.py` simultaneously.


## Glue Crawler and Athena

After data has been sent stored in the bucket, a Glue Crawler was used to obtain the data from the bucket.
This data was then queried through Athena as shown in the screenshot below.
![Screen Shot 2023-12-09 at 2 26 17 PM](https://github.com/MinaBasem/San-Francisco-Fires-Pipeline/assets/42482261/53359c1f-9678-4c9e-9fc4-5067b67b4361)







