import os
from os.path import join, dirname
from dotenv import load_dotenv
import pymysql
from kafka import KafkaConsumer
import json
from py2neo import Graph
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

mongo_host = os.environ.get('MONGO_HOST')
mongo_port = os.environ.get('MONGO_PORT')
mongo_db_name = os.environ.get('MONGO_DATABASE')
mongo_collection_name = os.environ.get('MONGO_BANDS_COLLECTION')
mongo_username = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')

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
    mongo_client = MongoClient(
        f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/"
    )
    mongo_collection = mongo_client[mongo_db_name][mongo_collection_name]
    print("Connected to MongoDB successfully!")

except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

try: 
    mysql_connection = pymysql.connect(host=mysql_host, port=int(mysql_port), user=mysql_user, password=mysql_password, database=mysql_db)
    mysql_cursor = mysql_connection.cursor()
    print("Connected to MySQL successfully!")
except Exception as e:
    print(f"Error connecting to MySQL: {e}")

users = []

try:
    # Kafka connection
    consumer = KafkaConsumer(*[kafka_bands_topic, kafka_users_topic],
                            bootstrap_servers=kafka_bootstrap_servers,
                            auto_offset_reset='earliest',  # You can set to 'latest' or 'earliest' based on your requirement
                            enable_auto_commit=True,
                            value_deserializer=lambda v: json.loads(v.decode('utf-8')))
    print("Connected to Kafka successfully!")
    print("Consuming messages...")

    for message in consumer:
        if message.topic == "users-topic":
            users = message.value

        for user_info in users:
            user = user_info['name']
            favorite_bands = user_info['favorite_bands']

            for band in favorite_bands:
                band_details = mongo_collection.find_one({"band_name": band})
                if band_details:
                    band_id = str(band_details["_id"])
                    band_name = band_details["band_name"]
                    band_albums = band_details["albums"]

                    # Insert bands
                    mysql_cursor.execute("INSERT INTO bands (BandID, BandName) VALUES (%s, %s) ON DUPLICATE KEY UPDATE BandName=%s",
                                        (band_id, band_name, band_name))

                    # Insert users
                    mysql_cursor.execute("INSERT INTO users (UserName, BandID) VALUES (%s, %s) ON DUPLICATE KEY UPDATE UserName=%s",
                                        (user, band_id, user))

                    # Insert albums
                    for album in band_albums:
                        mysql_cursor.execute("INSERT INTO albums (BandID, AlbumName, ReleaseDate) VALUES (%s, %s, %s)",
                                            (band_id, album["album_name"], album["release_date"]))

            # Commit the changes
            mysql_connection.commit()
            print({"message": "Wrote data to MySQL successfully", "data": user_info})
except Exception as e:
    print(f"Error: {e}")