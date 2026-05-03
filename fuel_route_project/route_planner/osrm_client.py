import requests
from django.conf import settings


def get_route(start_lat: float, start_lon: float,
              end_lat: float, end_lon: float) -> dict:

   
    coords = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    url = f"{settings.OSRM_BASE_URL}/route/v1/driving/{coords}"

    params = {
        'overview': 'full',       
        'geometries': 'geojson',   
        'steps': 'false',          
    }

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get('code') != 'Ok' or not data.get('routes'):
        raise ValueError("OSRM could not find a route between those locations.")

    route = data['routes'][0]
    distance_meters = route['distance']
    distance_miles = distance_meters * 0.000621371

    geometry_coords = route['geometry']['coordinates']  

    return {
        'distance_miles': round(distance_miles, 2),
        'geometry': geometry_coords,
    }