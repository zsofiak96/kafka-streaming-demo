import logging
import os
from confluent_kafka.admin import AdminClient, NewTopic
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)


def create_kafka_topics(
    topics: list[NewTopic],
    bootstrap_servers: str = os.getenv("BOOTSTRAP_SERVERS"),
) -> None:
    admin_client = AdminClient({"bootstrap.servers": bootstrap_servers})

    admin_client_create_topics_future = admin_client.create_topics(topics)

    for topic, future in admin_client_create_topics_future.items():
        try:
            future.result()
            logging.info(f"Topic {topic} created")
        except Exception as error:
            logging.error(f"Failed to create topic {topic}", exc_info=error)
