# Kafka streaming demo documentation

## Local development set up

### Virtual environment
This project uses [poetry](https://python-poetry.org/) for packaging and dependency management.
`poetry` created a brand new virtual environment isolated from the globale Python installation.
By default it  uses the Python version used during its installation.

To create and/or spawn a shell within the project's virtual environment use the following command:
```bash
poetry shell
```

To exit the shell run:
```bash
exit
```

### Documentation
The project documentation uses Github Pages. The site is currently being built from the `/docs` folder in the `main` branch.


### Testing docker
The `docker-compose.yml` file sets up a single-node `Kafka` broker. It configures the `Kafka` broker and controller listeners,
exposes the necessary ports, and mounts a local directory to persist `Kafka` data.

The broker runs in `Kraft` mode, eliminating the need for `Zookeeper`. `ZooKeeper` was traditionally used in `Kafka` to manage and coordinate the distributed brokers, handle leader elections, and maintain configuration and state information for topics and partitions.

Start the Kafka broker:
```bash
docker-compose up -d
```

Stop the Kafka broker:
```bash
docker-compose down --rmi local
```

#### Environment variable configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `KAFKA_KRAFT_MODE` | `true` | enable `Kafka` Raft (~`KRaft`) mode |
| `KAFKA_NODE_ID` | `1` | unique identifier for the `Kafka` broker within the cluster |
| `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP` | `CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT` | maps listener names to security protocols |
| `KAFKA_LISTENERS` | `CONTROLLER://0.0.0.0:9093,PLAINTEXT://0.0.0.0:9092` | the broker will listen for controller communication on port `9093` and for client communication on port `9092` |
| `KAFKA_ADVERTISED_LISTENERS` | `PLAINTEXT://localhost:9092` | clients will connect to the broker using `localhost:9092` |
| `KAFKA_INTER_BROKER_LISTENER_NAME` | `PLAINTEXT` | the listener that brokers will use to communicate with each other |
| `KAFKA_LOG_DIRS` | `/var/lib/kafka/data` | the directory where `Kafka` will store its log data |
| `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR` | `1` | the replication factor for the offsets (single-node setup) |
| `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR` | `1` | the replication factor for the [transaction state](https://kafka.apache.org/documentation/#upgrade_11_exactly_once_semantics) log topic (single-node setup) |
| `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR` | `1` | the minimum in-sync replicas for the [transaction state](https://kafka.apache.org/documentation/#upgrade_11_exactly_once_semantics) log topic (single-node setup) |
| `KAFKA_AUTO_CREATE_TOPICS_ENABLE` | `true` | enable automatic creation of topics when a non-existent topic is requested |
| `KAFKA_PROCESS_ROLES` | `broker,controller` | the process will act as both a broker and a controller |
| `KAFKA_CONTROLLER_QUORUM_VOTERS` | `1@localhost:9093` | the quorum voters for the controller: the controller with `KAFKA_NODE_ID == 1` will listen on `localhost:9093` |
| `KAFKA_CONTROLLER_LISTENER_NAMES` | `CONTROLLER` | the listener names that the controller will use |
| `KAFKA_LOG_MESSAGE_FORMAT_VERSION` | `3.0` | the log message format version |
| `KAFKA_CONFLUENT_SUPPORT_METRICS_ENABLE` | `false` | disable the collection of `Confluent` support metrics |
| `CLUSTER_ID` | `kafka-streaming-demo-cluster` |  the unique identifier of the `Kafka` broker |
