import os
from os.path import join, dirname
from dotenv import load_dotenv
from kafka import KafkaProducer
from flask import Flask, request, jsonify
from pymongo import MongoClient
from py2neo import Graph
import json

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

mongo_host = os.environ.get('MONGO_HOST')
mongo_port = os.environ.get('MONGO_PORT')
mongo_db_name = os.environ.get('MONGO_DATABASE')
mongo_collection_name = os.environ.get('MONGO_BANDS_COLLECTION')
mongo_username = os.environ.get('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD')

neo4j_host = os.environ.get('NEO4J_HOST')
neo4j_port = os.environ.get('NEO4J_PORT')
neo4j_username = os.environ.get('NEO4J_AUTH').split('/')[0]
neo4j_password = os.environ.get('NEO4J_AUTH').split('/')[1]
neo4j_uri = "bolt://" + neo4j_host + ':' + neo4j_port

kafka_host = os.environ.get('KAFKA_HOST')
kafka_port = os.environ.get('KAFKA_PORT')
kafka_bootstrap_servers = kafka_host + ':' + kafka_port
kafka_bands_topic = os.environ.get('KAFKA_BANDS_TOPIC')
kafka_users_topic = os.environ.get('KAFKA_USERS_TOPIC')
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
    # Neo4j connection
    graph = Graph(neo4j_uri, auth=(neo4j_username, neo4j_password))
    print("Connected to Neo4j successfully!")

except Exception as e:
    print(f"Error connecting to Neo4j: {e}")

try:
    # Kafka connection
    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("Connected to Kafka successfully!")

except Exception as e:
    print(f"Error connecting to Kafka: {e}")

@app.route('/publish/bands', methods=['POST'])
def mongo_producer():
    start_date = request.json['start_date']
    end_date = request.json['end_date']

    bands_query = {"formation_date": {"$gte": start_date, "$lte": end_date}}
    bands = list(mongo_collection.find(bands_query))    

    for band in bands:
        band["_id"] = str(band["_id"]) # Remove ObjectID type
    
    producer.send(kafka_bands_topic, value=bands)

    return jsonify({"message": "Bands published to Kafka successfully"})

@app.route('/publish/users', methods=['POST'])
def graph_producer():
    user_name = request.json['user_name']

    try:
    # Neo4j query to retrieve user and friends by name
        query = f"""
        MATCH (u:User)-[:FRIEND]->(friend)
        WHERE u.name = '{user_name}'
        RETURN u, friend
        """
        result = graph.run(query)

        # Collect users to publish
        users_to_publish = []
        for record in result:
            user = record['u']
            friend = record['friend']
            users_to_publish.append({
                "user_name": user['name'],
                "friend_name": friend['name']
            })

        producer.send(kafka_users_topic, value=users_to_publish)

        return jsonify({"message": "Users published to Kafka successfully"})

    except Exception as e:
        return jsonify({"error": f"Error processing request: {e}"})

if __name__ == '__main__':
    app.run(debug=True)
