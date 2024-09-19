import logging
import os
import schedule
import time
from dotenv import load_dotenv

import requests
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer

from constants import (
    WEATHER,
)
from models import RawData, RawDataKey, RequestParameters

import pandas as pd

load_dotenv()

logging.basicConfig(level=logging.INFO)


kafka_config = {"bootstrap.servers": os.getenv("BOOTSTRAP_SERVERS")}
admin_client = AdminClient(kafka_config)
kafka_topic_config = {"retention.ms": 24 * 60 * 60 * 1000}  # ~ 1day


def fetch_open_weather_map_api(
    parameters: RequestParameters,
    base_url: str = "https://api.openweathermap.org/data/2.5/weather",
) -> RawData | None:
    """Fetch OpenWeatherMap API and parse response into a RawData model.

    :param parameters: endpoint specific request parameters
    :param base_url: defaults to "https://api.openweathermap.org/data/2.5/weather"
    """
    response = requests.get(base_url, params=parameters)
    match response.status_code:
        case 200:
            data = response.json()
            normalized_data = pd.json_normalize(
                data,
                sep="_",
            )
            normalized_data = pd.concat(
                [
                    normalized_data.drop(columns=[WEATHER]),
                    pd.json_normalize(normalized_data[WEATHER][0]).add_prefix(
                        f"{WEATHER}_"
                    ),
                ],
                axis=1,
            ).to_dict(orient="records")[0]
            raw_data = RawData(**normalized_data)
        case _:
            raw_data = None
            logging.info(
                f"Check your API configuration. Open Weather Map responded with {response.status_code}"
            )
    return raw_data


def main() -> None:
    """The main producer task. Fetch API for Vienna area
    and produce to the `weather` topic.
    """
    raw_data = fetch_open_weather_map_api(
        parameters=RequestParameters(
            lat=48.21,
            lon=16.36,
        )
    )

    producer = Producer(kafka_config)
    producer.produce(
        WEATHER,
        key=RawDataKey(
            latitude=raw_data.latitude, longitude=raw_data.longitude
        ).model_dump_json(),
        value=raw_data.model_dump_json(),
    )
    producer.flush()


if __name__ == "__main__":
    if WEATHER not in admin_client.list_topics().topics.keys():
        admin_client.create_topics(
            [
                NewTopic(
                    WEATHER,
                    num_partitions=1,
                    replication_factor=1,
                    config=kafka_topic_config,
                )
            ]
        )

    schedule.every(10).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
