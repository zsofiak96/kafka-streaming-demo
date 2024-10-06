import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class RawData(BaseModel):
    atmospheric_pressure_on_ground_level_in_hpa: float = Field(alias="main_grnd_level")
    atmospheric_pressure_on_sea_level_in_hpa: float = Field(alias="main_pressure")
    city_name: str = Field(alias="name")
    cloudiness_in_percentage: float = Field(alias="clouds_all")
    country: str = Field(alias="sys_country")
    humidity_in_percentage: float = Field(alias="main_humidity")
    latitude: float = Field(alias="coord_lat")
    longitude: float = Field(alias="coord_lon")
    rain_in_mm_per_h: float | None = Field(alias="rain_1h", default=None)
    snow_in_mm_per_h: float | None = Field(alias="snow_1h", default=None)
    sunrise_as_unix_timestamp_in_utc: int = Field(alias="sys_sunrise")
    sunset_as_unix_timestamp_in_utc: int = Field(alias="sys_sunset")
    temperature_feels_like_in_celsius: float = Field(alias="main_feels_like")
    temperature_in_celsius: float = Field(alias="main_temp")
    temperature_max_in_celsius: float = Field(alias="main_temp_max")
    temperature_min_in_celsius: float = Field(alias="main_temp_min")
    time_of_data_calculation_as_unix_timestamp_in_utc: int = Field(alias="dt")
    timezone_shift_in_seconds_from_utc: float = Field(alias="timezone")
    visibility_in_meter: float = Field(alias="visibility")
    weather_description: str = Field(alias="weather_description")
    weather_group: str = Field(alias="weather_main")
    wind_direction_in_degrees: float = Field(alias="wind_deg")
    wind_speed_in_meter_per_second: float = Field(alias="wind_speed")


class RawDataKey(BaseModel):
    latitude: float
    longitude: float


class RequestParameters(BaseModel):
    lat: float
    lon: float
    units: str = "metric"
    appid: str = os.getenv("OPEN_WEATHER_API_KEY", None)
