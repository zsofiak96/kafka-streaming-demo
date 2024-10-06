import logging
import os
import schedule
import time
from dotenv import load_dotenv

import requests
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer

from admin import create_kafka_topics
from constants import (
    WEATHER,
)
from models import RawData, RawDataKey, RequestParameters

import pandas as pd

load_dotenv()

logging.basicConfig(level=logging.INFO)

NUM_PARTITIONS = 6

kafka_config = {"bootstrap.servers": os.getenv("BOOTSTRAP_SERVERS")}
admin_client = AdminClient(kafka_config)
request_coordinates = {
    "Klagenfurt": RawDataKey(latitude=46.63, longitude=14.31),
    "Salzburg": RawDataKey(latitude=47.81, longitude=13.03),
    "Graz": RawDataKey(latitude=47.07, longitude=15.42),
    "Vienna": RawDataKey(latitude=48.21, longitude=16.36),
    "Innsbruck": RawDataKey(latitude=47.25, longitude=11.4),
    "Linz": RawDataKey(latitude=48.30, longitude=14.28),
}


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


def check_success(err, msg):
    if err is not None:
        print(f"Failed to deliver message:\n" f"msg -> {msg}\n" f"error -> {err}")
    else:
        print(
            f"Message with key {msg.key()} was produced to topic {msg.topic()} to partition {msg.partition()}"
        )


def main() -> None:
    """The main producer task. Fetch API for Vienna area
    and produce to the `weather` topic.
    """
    producer = Producer(kafka_config)
    for request_key, request_value in request_coordinates.items():
        raw_data = fetch_open_weather_map_api(
            parameters=RequestParameters(
                lat=request_value.latitude,
                lon=request_value.longitude,
            )
        )
        producer.produce(
            WEATHER,
            key=request_key,
            value=raw_data.model_dump_json(),
            callback=check_success,
            headers={"city_name": request_key},
        )

        logging.info(f"Produced values with key: {request_key}")

        producer.flush()


if __name__ == "__main__":
    create_kafka_topics(
        [
            NewTopic(
                WEATHER,
                num_partitions=NUM_PARTITIONS,
                replication_factor=1,
                config={"retention.ms": 24 * 60 * 60 * 1000},
            )
        ]
    )

    schedule.every(0.25).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
