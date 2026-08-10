import requests
import ssl
import streamlit as st
from requests.adapters import HTTPAdapter

STATION_ID = "CAAH60"  # your CWA station
MOENV_SITE_NAME = "古亭"  # your Ministry of Environment AQI station

class CWAAdapter(HTTPAdapter):
    """Custom adapter that relaxes strict X.509 checking for CWA's cert chain."""
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)

@st.cache_data(ttl=600)
def get_outdoor_conditions():
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
    params = {
        "Authorization": st.secrets["CWA_API_KEY"],
        "StationId": STATION_ID,
    }

    session = requests.Session()
    session.mount("https://opendata.cwa.gov.tw", CWAAdapter())

    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        station = data["records"]["Station"][0]
        weather_elem = station["WeatherElement"]

        return {
            "temperature": float(weather_elem["AirTemperature"]),
            "humidity": float(weather_elem["RelativeHumidity"]),
            "weather_desc": weather_elem.get("Weather", ""),
            "station_name": station["StationName"],
            "obs_time": station["ObsTime"]["DateTime"],
        }
    except (requests.RequestException, KeyError, ValueError, IndexError) as e:
        st.warning(f"Couldn't fetch outdoor weather data: {e}")
        return None


@st.cache_data(ttl=600)
def get_outdoor_pm25():
    url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
    params = {
        "api_key": st.secrets["MOENV_API_KEY"],
        "limit": 1000,
        "sort": "ImportDate desc",
        "format": "json",
    }

    session = requests.Session()
    session.mount("https://data.moenv.gov.tw", CWAAdapter())

    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        records = data if isinstance(data, list) else data.get("records", [])
        site_record = next(
            (r for r in records if r.get("sitename") == MOENV_SITE_NAME), None
        )

        if not site_record:
            return None

        return {
            "site_name": site_record.get("sitename"),
            "pm2_5": float(site_record.get("pm2.5", 0)),
            "pm2_5_avg": float(site_record.get("pm2.5_avg", 0)),
            "aqi": int(site_record.get("aqi", 0)),
            "status": site_record.get("status"),
            "publish_time": site_record.get("publishtime"),
        }
    except (requests.RequestException, KeyError, ValueError, StopIteration) as e:
        st.warning(f"Couldn't fetch outdoor PM2.5 data: {e}")
        return None