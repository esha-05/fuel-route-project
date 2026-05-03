import os
import math
import logging
import pandas as pd
from django.conf import settings

logger = logging.getLogger(__name__)

USCITIES_CSV = os.path.join(settings.BASE_DIR, 'uscities.csv')

# State name mapping
STATE_ABBR = {
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA',
    'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD',
    'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
    'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC',
    'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY',
    'DC'
}


def haversine_miles(lat1, lon1, lat2, lon2) -> float:
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.asin(math.sqrt(a))


_city_lookup = None

def _get_city_lookup() -> dict:
    global _city_lookup
    if _city_lookup is not None:
        return _city_lookup

    _city_lookup = {}
    if not os.path.exists(USCITIES_CSV):
        logger.error(f"uscities.csv not found at {USCITIES_CSV}")
        return _city_lookup

    df = pd.read_csv(USCITIES_CSV, usecols=['city', 'state_id', 'lat', 'lng'])
    for _, row in df.iterrows():
        key = (str(row['city']).strip().lower(), str(row['state_id']).strip().upper())
        _city_lookup[key] = (float(row['lat']), float(row['lng']))

    logger.info(f"Loaded {len(_city_lookup)} US cities for geocoding.")
    return _city_lookup


def _geocode_city_state(city: str, state: str):
    lookup = _get_city_lookup()
    key = (city.strip().lower(), state.strip().upper())
    return lookup.get(key)


_stations = None


def _build_stations() -> list[dict]:
    df = pd.read_csv(settings.FUEL_PRICES_CSV)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=['Retail Price', 'City', 'State'])
    df['City'] = df['City'].str.strip()
    df['State'] = df['State'].str.strip()

    stations = []
    not_found = 0

    for _, row in df.iterrows():
        coords = _geocode_city_state(row['City'], row['State'])
        if coords:
            stations.append({
                'name': row['Truckstop Name'],
                'city': row['City'],
                'state': row['State'],
                'price': float(row['Retail Price']),
                'lat': coords[0],
                'lon': coords[1],
            })
        else:
            not_found += 1

    logger.info(f"Loaded {len(stations)} stations. {not_found} cities not found.")
    return stations


def get_stations() -> list[dict]:
    global _stations
    if _stations is None:
        _stations = _build_stations()
    return _stations


def find_cheapest_nearby(lat: float, lon: float, radius_miles: float = 50) -> dict | None:
    stations = get_stations()
    candidates = []

    for s in stations:
        d = haversine_miles(lat, lon, s['lat'], s['lon'])
        if d <= radius_miles:
            candidates.append({**s, 'distance_from_point': round(d, 2)})

    if not candidates:
        return None

    candidates.sort(key=lambda x: (x['price'], x['distance_from_point']))
    return candidates[0]