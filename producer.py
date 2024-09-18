import logging
import os
import schedule
import time
from dotenv import load_dotenv

import requests
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer

from constants import (
    ALL,
    CLOUDS,
    COUNTRY,
    DEG,
    DT,
    FEELS_LIKE,
    GRND_LEVEL,
    HUMIDITY,
    MAIN,
    PRESSURE,
    SEA_LEVEL,
    SPEED,
    SUNRISE,
    SUNSET,
    SYS,
    TEMP,
    TEMP_MAX,
    TEMP_MIN,
    VISIBILITY,
    WEATHER,
    WIND,
)
from models import RawData, RequestParameters

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
    response = requests.get(base_url, params=parameters)
    match response.status_code:
        case 200:
            data = response.json()
            normalized_data = pd.json_normalize(
                data,
                record_path=[WEATHER],
                meta=[
                    DT,
                    [MAIN, TEMP],
                    [MAIN, FEELS_LIKE],
                    [MAIN, TEMP_MIN],
                    [MAIN, TEMP_MAX],
                    [MAIN, PRESSURE],
                    [MAIN, SEA_LEVEL],
                    [MAIN, GRND_LEVEL],
                    [MAIN, HUMIDITY],
                    [VISIBILITY],
                    [WIND, SPEED],
                    [WIND, DEG],
                    [CLOUDS, ALL],
                    [SYS, COUNTRY],
                    [SYS, SUNRISE],
                    [SYS, SUNSET],
                ],
                sep="_",
                record_prefix=f"{WEATHER}_",
            ).to_dict(orient="records")[0]
            raw_data = RawData(**normalized_data)
        case _:
            raw_data = None
            logging.info(
                f"Check your API configuration. Open Weather Map reported {response.status_code}"
            )
    return raw_data


def main() -> None:
    raw_data = fetch_open_weather_map_api(
        parameters=RequestParameters(
            lat=48.21,
            lon=16.36,
        )
    )

    producer = Producer(kafka_config)
    producer.produce(WEATHER, raw_data.model_dump_json())
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

    schedule.every(5).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
