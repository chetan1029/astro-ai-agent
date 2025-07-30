from typing import Tuple

from geopy import GoogleV3
from geopy.exc import GeocoderServiceError
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from datetime import datetime
from app.src.core.config import get_settings


GOOGLE_API_KEY = get_settings().google_api_key

def convert_to_utc(dob_local: datetime, lat: float, lon: float) -> datetime:
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lat=lat, lng=lon)
    tz = ZoneInfo(tz_str)
    local_dt = dob_local.replace(tzinfo=tz)
    return local_dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)


def get_lat_long_by_address(address: str) -> Tuple[str, float, float]:
    try:
        geolocator = GoogleV3(api_key=GOOGLE_API_KEY, timeout=10)
        location = geolocator.geocode(address)
        if location:
            return location.address, location.latitude, location.longitude
        raise ValueError(f"Could not geocode address: {address}")
    except GeocoderServiceError as e:
        raise RuntimeError(f"Geocoding service failed: {e}")
