import os
from os.path import join, dirname
from dotenv import load_dotenv
import pymysql
from kafka import KafkaConsumer
import json

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

kafka_host = os.environ.get('KAFKA_HOST')
kafka_port = os.environ.get('KAFKA_PORT')
kafka_bootstrap_servers = kafka_host + ':' + kafka_port
kafka_bands_topic = os.environ.get('KAFKA_BANDS_TOPIC')
kafka_users_topic = os.environ.get('KAFKA_USERS_TOPIC')

mysql_host = os.environ.get('MYSQL_HOST')
mysql_port = os.environ.get('MYSQL_PORT')
mysql_user = os.environ.get('MYSQL_USER')
mysql_password = os.environ.get('MYSQL_PASSWORD')
mysql_db = os.environ.get('MYSQL_DATABASE')

try:
    # Kafka connection
    consumer = KafkaConsumer(*[kafka_bands_topic, kafka_users_topic],
                            bootstrap_servers=kafka_bootstrap_servers,
                            auto_offset_reset='earliest',  # You can set to 'latest' or 'earliest' based on your requirement
                            enable_auto_commit=True,
                            value_deserializer=lambda v: json.loads(v.decode('utf-8')))
    print("Connected to Kafka successfully!")

    try: 
        mysql_connection = pymysql.connect(host=mysql_host, port=int(mysql_port), user=mysql_user, password=mysql_password, database=mysql_db)
        mysql_cursor = mysql_connection.cursor()
        print("Connected to MySQL successfully!")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")

    for message in consumer:
        # Process the received message
        if message.topic == 'users-topic':
            print(message)
        if message.topic == 'bands-topic':
            print(message)
    
    # Close the consumer when done
    consumer.close()

except Exception as e:
    print(f"Error connecting to Kafka: {e}")

