import os
from os.path import join, dirname
from dotenv import load_dotenv
from kafka import KafkaProducer
from flask import Flask, request, jsonify
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

mongo_host = os.environ.get('MONGO_HOST')
mongo_port = os.environ.get('MONGO_PORT')
mongo_db_name = os.environ.get('MONGO_DATABASE')
mongo_collection_name = os.environ.get('MONGO_BANDS_COLLECTION')
mongo_username = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')

kafka_host = os.environ.get('KAFKA_HOST')
kafka_port = os.environ.get('KAFKA_PORT')
kafka_bootstrap_servers = kafka_host + ':' + kafka_port
kafka_topic = os.environ.get('KAFKA_BANDS_TOPIC')
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,
                         value_serializer=lambda v: str(v).encode('utf-8'))

try:
    mongo_client = MongoClient(
        f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/"
    )
    mongo_collection = mongo_client[mongo_db_name][mongo_collection_name]
    print("Connected to MongoDB successfully!")

except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

try:
    # Kafka connection
    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers,
        value_serializer=lambda v: str(v).encode('utf-8')
    )
    print("Connected to Kafka successfully!")

except Exception as e:
    print(f"Error connecting to Kafka: {e}")

@app.route('/publish/bands', methods=['POST'])
def publish_bands_to_kafka():
    start_date = request.json['start_date']
    end_date = request.json['end_date']

    bands_query = {"formation_date": {"$gte": start_date, "$lte": end_date}}
    bands = list(mongo_collection.find(bands_query))

    for band in bands:
        producer.send(kafka_topic, value=band)

    return jsonify({"message": "Bands published to Kafka successfully"})


if __name__ == '__main__':
    app.run(debug=True)
