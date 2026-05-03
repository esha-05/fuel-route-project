import math
from .fuel_data import haversine_miles, find_cheapest_nearby
from django.conf import settings


MAX_RANGE = settings.VEHICLE_MAX_RANGE_MILES   
MPG = settings.VEHICLE_MPG                     

FUEL_TRIGGER_MILES = 400   # = 80% of 500


def _interpolate_distance(geometry: list) -> list[tuple[float, float, float]]:
    result = []
    cumulative = 0.0
    prev_lat, prev_lon = None, None

    for point in geometry:
        lon, lat = point[0], point[1]
        if prev_lat is not None:
            seg_dist = haversine_miles(prev_lat, prev_lon, lat, lon)
            cumulative += seg_dist
        result.append((lon, lat, cumulative))
        prev_lat, prev_lon = lat, lon

    return result


def plan_fuel_stops(geometry: list, total_distance_miles: float) -> dict:
    path = _interpolate_distance(geometry)
    total_path_miles = path[-1][2]

    fuel_stops = []
    miles_since_last_fill = 0.0
    last_fill_distance = 0.0
    stop_number = 0

    SEARCH_WINDOW_MILES = 80   
    CANDIDATE_STEP = 20       

    i = 0
    while i < len(path):
        lon, lat, cum_dist = path[i]
        miles_since_last_fill = cum_dist - last_fill_distance
        remaining_range = MAX_RANGE - miles_since_last_fill
        remaining_route = total_path_miles - cum_dist

    
        if remaining_range <= (MAX_RANGE - FUEL_TRIGGER_MILES) and remaining_route > 10:
    
            candidates = []
            for j in range(i, len(path)):
                _, _, cd = path[j]
                if cd - cum_dist > SEARCH_WINDOW_MILES:
                    break
                if (cd - cum_dist) % CANDIDATE_STEP < 5:  
                    candidates.append(path[j])

            if not candidates:
                candidates = [path[i]]

            best_stop = None
            best_price = float('inf')
            best_point = None

            for clon, clat, cdist in candidates:
                station = find_cheapest_nearby(clat, clon, radius_miles=50)
                if station and station['price'] < best_price:
                    best_price = station['price']
                    best_stop = station
                    best_point = (clon, clat, cdist)

            if best_stop and best_point:
                stop_number += 1
                fill_dist = best_point[2]
                gallons = (fill_dist - last_fill_distance) / MPG
                cost = round(gallons * best_stop['price'], 2)

                fuel_stops.append({
                    'stop_number': stop_number,
                    'station_name': best_stop['name'],
                    'city': best_stop['city'],
                    'state': best_stop['state'],
                    'lat': best_stop['lat'],
                    'lon': best_stop['lon'],
                    'price_per_gallon': best_stop['price'],
                    'gallons_purchased': round(gallons, 2),
                    'cost': cost,
                    'miles_from_start': round(fill_dist, 2),
                })

                last_fill_distance = fill_dist
                
                while i < len(path) and path[i][2] < fill_dist:
                    i += 1
                continue

        i += 1


    final_leg = total_path_miles - last_fill_distance
    final_gallons = final_leg / MPG
    total_gallons = sum(s['gallons_purchased'] for s in fuel_stops) + final_gallons
    total_cost = sum(s['cost'] for s in fuel_stops)

    if fuel_stops:
        last_price = fuel_stops[-1]['price_per_gallon']
    else:

        mid = path[len(path) // 2]
        station = find_cheapest_nearby(mid[1], mid[0], radius_miles=100)
        last_price = station['price'] if station else 3.50

    total_cost += round(final_gallons * last_price, 2)

    return {
        'fuel_stops': fuel_stops,
        'total_gallons': round(total_gallons, 2),
        'total_fuel_cost': round(total_cost, 2),
    }