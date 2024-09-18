import os
from datetime import datetime

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class RawData(BaseModel):
    clouds_all: float
    dt: datetime
    main_feels_like: float
    main_grnd_level: float
    main_humidity: float
    main_pressure: float
    main_sea_level: float
    main_temp_max: float
    main_temp_min: float
    main_temp: float
    sys_country: str
    sys_sunrise: int
    sys_sunset: int
    visibility: float
    weather_description: str
    weather_icon: str
    weather_id: int
    weather_main: str
    wind_deg: float
    wind_speed: float


class RequestParameters(BaseModel):
    lat: float
    lon: float
    unit: str = "metric"
    appid: str = os.getenv("API_KEY", None)
