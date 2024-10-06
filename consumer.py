import argparse
import json
from confluent_kafka.cimpl import NewTopic
from pyspark.sql.functions import from_json, col, window, array, struct, lit, encode
from pyspark.sql.types import (
    StructType,
    StructField,
    FloatType,
    StringType,
    IntegerType,
)

from admin import create_kafka_topics
from constants import WEATHER
from pyspark.sql import SparkSession
import os
from dotenv import load_dotenv


load_dotenv()


weather_schema = StructType(
    [
        StructField(
            "atmospheric_pressure_on_ground_level_in_hpa", FloatType(), nullable=False
        ),
        StructField(
            "atmospheric_pressure_on_ground_level_in_hpa", FloatType(), nullable=False
        ),
        StructField("city_name", StringType(), nullable=False),
        StructField("cloudiness_in_percentage", FloatType(), nullable=False),
        StructField("country", StringType(), nullable=False),
        StructField("humidity_in_percentage", FloatType(), nullable=False),
        StructField("latitude", FloatType(), nullable=False),
        StructField("longitude", FloatType(), nullable=False),
        StructField("rain_in_mm_per_h", FloatType()),
        StructField("snow_in_mm_per_h", FloatType()),
        StructField("sunrise_as_unix_timestamp_in_utc", IntegerType(), nullable=False),
        StructField("sunset_as_unix_timestamp_in_utc", IntegerType(), nullable=False),
        StructField("temperature_feels_like_in_celsius", FloatType(), nullable=False),
        StructField("temperature_in_celsius", FloatType(), nullable=False),
        StructField("temperature_max_in_celsius", FloatType(), nullable=False),
        StructField("temperature_min_in_celsius", FloatType(), nullable=False),
        StructField(
            "time_of_data_calculation_as_unix_timestamp_in_utc",
            FloatType(),
            nullable=False,
        ),
        StructField("timezone_shift_in_seconds_from_utc", FloatType(), nullable=False),
        StructField("visibility_in_meter", FloatType(), nullable=False),
        StructField("weather_description", StringType(), nullable=False),
        StructField("weather_group", StringType(), nullable=False),
        StructField("wind_direction_in_degrees", FloatType(), nullable=False),
        StructField("wind_speed_in_meter_per_second", FloatType(), nullable=False),
    ]
)


def main(partitions: list[int]):
    create_kafka_topics(
        [
            NewTopic(
                f"{WEATHER}-processed",
                num_partitions=1,
                replication_factor=1,
                config={"retention.ms": 24 * 60 * 60 * 1000},
            )
        ]
    )
    spark = (
        SparkSession.builder.appName("weather-consumer")
        .master("local[*]")
        .config(
            "spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2"
        )
        .config("spark.sql.adaptive.enabled", "false")
        .getOrCreate()
    )

    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", os.getenv("BOOTSTRAP_SERVERS"))
        .option("assign", json.dumps({WEATHER: partitions}))
        .load()
    )

    df_timestamp_value_json = df.selectExpr("timestamp", "CAST(value AS STRING)")

    df_timestamp_value_json_exploded = df_timestamp_value_json.withColumn(
        "value", from_json(col("value"), weather_schema)
    )

    df_timestamp_value_json_exploded = df_timestamp_value_json_exploded.select(
        [col("timestamp"), col("value.*")]
    )

    df_group_count_by_city_name = df_timestamp_value_json_exploded.groupBy(
        window("timestamp", "1 minute"), "city_name"
    ).count()

    df_with_headers = df_group_count_by_city_name.withColumn(
        "headers",
        array(
            struct(
                lit("city_name").alias("key"),
                encode(col("city_name"), "utf-8").alias("value"),
            )
        ),
    )

    df_with_headers = df_with_headers.withColumn("timestamp", col("window.end"))

    query = (
        df_with_headers.selectExpr(
            "to_json(struct(timestamp, count)) AS value", "headers AS headers"
        )
        .writeStream.outputMode("complete")
        .format("kafka")
        .option("kafka.bootstrap.servers", os.getenv("BOOTSTRAP_SERVERS"))
        .option("topic", f"{WEATHER}-processed")
        .option(
            "checkpointLocation",
            f"checkpoint-location-{'-'.join([str(partition) for partition in partitions])}",
        )
        .option("includeHeaders", "true")
        .start()
    )

    query.awaitTermination()

    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"Process kafka stream with topic '{WEATHER}'"
    )
    parser.add_argument(
        "-p",
        "--partitions",
        dest="partitions",
        nargs="+",
        type=int,
        help="specific partition(s) to consume",
    )

    args = parser.parse_args()
    main(args.partitions)
