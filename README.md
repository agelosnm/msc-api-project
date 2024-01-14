# Docker Compose Configuration

This Docker Compose configuration file (`docker-compose.yml`) sets up a development environment with containers for MySQL, Neo4j, MongoDB, Kafka, and Zookeeper. These containers can be used individually or together, depending on your application requirements.

## Services

- ### MySQL
- ### Neo4j
- ### MongoDB
- ### Kafka (needs Zookeeper)

## Volumes

- **mysql_data:** MySQL data volume
- **mongo_data:** MongoDB data volume
- **neo4j_data:** Neo4j data volume

## Usage

1. Make sure you have Docker and Docker Compose installed.
2. Create an `.env` file with the required environment variables (refer to `.env.example` file).
3. Run `docker compose up -d` to start the services.

Feel free to customize the configuration based on your specific needs.