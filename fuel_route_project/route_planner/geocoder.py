import requests
from django.conf import settings

import requests
from django.conf import settings


def geocode(location: str) -> tuple[float, float]:
    headers = {'User-Agent': 'FuelRouteApp/1.0'}


    try:
        resp = requests.get(
            'https://photon.komoot.io/api/',
            params={'q': f"{location}, USA", 'limit': 1, 'lang': 'en'},
            headers=headers,
            timeout=10
        )
        data = resp.json()
        features = data.get('features', [])
        if features:
            coords = features[0]['geometry']['coordinates']
            lon, lat = coords[0], coords[1]
            return lat, lon
    except Exception:
        pass

    try:
        resp = requests.get(
            settings.NOMINATIM_URL,
            params={'q': location, 'format': 'json', 'limit': 1, 'countrycodes': 'us'},
            headers=headers,
            timeout=10
        )
        results = resp.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon'])
    except Exception:
        pass

    raise ValueError(f"Could not geocode location: '{location}'")