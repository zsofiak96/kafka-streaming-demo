import pytest
from models import RequestParameters
from producer import main, fetch_open_weather_map_api


@pytest.mark.skip(reason="Not implemented")
def test_fetch_open_weather_map_api() -> None:
    fetch_open_weather_map_api(
        parameters=RequestParameters(
            lat=48.21,
            lon=16.36,
        )
    )


@pytest.mark.skip(reason="Not implemented")
def test_main() -> None:
    main()
