# Docker Compose Configuration

This Docker Compose configuration file (`docker-compose.yml`) sets up a development environment with containers for MySQL, Neo4j, MongoDB, Kafka, and Zookeeper. These containers can be used individually or together, depending on your application requirements.

## Services

### MySQL

- **Container Name:** mysql
- **Restart Policy:** unless-stopped
- **Image:** mysql:8.0.33
- **Volumes:**
  - mysql-data: /var/lib/mysql
- **Environment Variables:**
  - MYSQL_ROOT_PASSWORD
  - MYSQL_DATABASE
- **Ports:**
  - 3306:3306
- **Environment File:** .env

### Neo4j

- **Container Name:** neo4j
- **Restart Policy:** unless-stopped
- **Image:** neo4j:5.15.0
- **Volumes:**
  - neo4j-data: /data
- **Environment Variables:**
  - NEO4J_AUTH
- **Ports:**
  - 7474:7474
  - 7687:7687

### MongoDB

- **Container Name:** mongo
- **Restart Policy:** unless-stopped
- **Image:** mongo:7.0.5
- **Volumes:**
  - mongo-data: /data/db
- **Environment Variables:**
  - MONGO_INITDB_ROOT_USERNAME
  - MONGO_INITDB_ROOT_PASSWORD
- **Ports:**
  - 27017:27017
- **Environment File:** .env
- **Command:** [--auth]

### Kafka

- **Container Name:** kafka
- **Restart Policy:** unless-stopped
- **Image:** confluentinc/cp-kafka:7.5.0
- **Ports:**
  - 9092:9092
- **Environment Variables:**
  - KAFKA_BROKER_ID: 1
  - KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
  - KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
  - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
  - KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
  - KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
  - KAFKA_ADVERTISED_HOST_NAME: kafka

### Zookeeper

- **Container Name:** zookeeper
- **Restart Policy:** unless-stopped
- **Image:** confluentinc/cp-zookeeper:7.5.0
- **Environment Variables:**
  - ZOOKEEPER_CLIENT_PORT: 2181
  - ZOOKEEPER_TICK_TIME: 2000

## Volumes

- **mysql-data:** MySQL data volume
- **mongo-data:** MongoDB data volume
- **neo4j-data:** Neo4j data volume

## Usage

1. Make sure you have Docker and Docker Compose installed.
2. Create an `.env` file with the required environment variables (refer to `.env.example` file).
3. Run `docker compose up -d` to start the services.

Feel free to customize the configuration based on your specific needs.