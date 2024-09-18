# Kafka Producer

The initial kafka producer fetches the [OpenWeather API](https://openweathermap.org/) every 5 minutes.
The raw data is written into a kafka stream with topic `weather`.

## Topic `weather` configuration

| Config | Value |
|--------|-------|
| Retention period | `24 hours` |
| Number of partitions | `1` |
| Number of replicas | `1` |
