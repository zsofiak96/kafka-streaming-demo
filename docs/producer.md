# Producer API

The initial kafka producer fetches the [OpenWeather API](https://openweathermap.org/) every 10 minutes.
The APi itself updates its data every 10 minutes.
The raw data is written into a kafka stream with topic `weather`.

## Topic `weather` configuration

| Config | Value |
|--------|-------|
| Retention period | `24 hours` |
| Number of partitions | `1` |
| Number of replicas | `1` |

## Data model

[RawData](https://github.com/zsofiak96/kafka-streaming-demo/blob/825bb3abf508442d78595e621587e7719b7b7389/models.py#L9)
