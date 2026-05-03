
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RouteRequestSerializer
from .geocoder import geocode
from .osrm_client import get_route
from .route_optimizer import plan_fuel_stops

logger = logging.getLogger(__name__)


class RoutePlannerView(APIView):

    def post(self, request):
        # Step 1: Validate input
        serializer = RouteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_str = serializer.validated_data['start']
        finish_str = serializer.validated_data['finish']

        # Step 2: Geocode both locations in parallel 
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_start = executor.submit(geocode, start_str)
                future_finish = executor.submit(geocode, finish_str)
                start_lat, start_lon = future_start.result(timeout=15)
                finish_lat, finish_lon = future_finish.result(timeout=15)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return Response({'error': 'Geocoding service unavailable.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Step 3: Get route from OSRM 
        try:
            route_data = get_route(start_lat, start_lon, finish_lat, finish_lon)
        except Exception as e:
            logger.error(f"OSRM error: {e}")
            return Response({'error': f'Routing service error: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        total_distance = route_data['distance_miles']
        geometry = route_data['geometry']

        # Step 4: Plan fuel stops 
        fuel_plan = plan_fuel_stops(geometry, total_distance)

        # Step 5: Build and return response
        response_data = {
            'start': start_str,
            'finish': finish_str,
            'start_coords': {'lat': start_lat, 'lon': start_lon},
            'finish_coords': {'lat': finish_lat, 'lon': finish_lon},
            'total_distance_miles': total_distance,
            'fuel_stops': fuel_plan['fuel_stops'],
            'total_fuel_stops': len(fuel_plan['fuel_stops']),
            'total_gallons': fuel_plan['total_gallons'],
            'total_fuel_cost': fuel_plan['total_fuel_cost'],
            'route_geometry': geometry,
        }

        return Response(response_data, status=status.HTTP_200_OK)