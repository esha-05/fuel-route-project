
from rest_framework import serializers


class RouteRequestSerializer(serializers.Serializer):
    start = serializers.CharField(
        max_length=200,
        help_text="Starting location within the USA (e.g. 'New York, NY')"
    )
    finish = serializers.CharField(
        max_length=200,
        help_text="Destination location within the USA (e.g. 'Los Angeles, CA')"
    )


class FuelStopSerializer(serializers.Serializer):
    stop_number = serializers.IntegerField()
    station_name = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    price_per_gallon = serializers.FloatField()
    gallons_purchased = serializers.FloatField()
    cost = serializers.FloatField()
    miles_from_start = serializers.FloatField()


class RouteResponseSerializer(serializers.Serializer):
    start = serializers.CharField()
    finish = serializers.CharField()
    start_coords = serializers.DictField()
    finish_coords = serializers.DictField()
    total_distance_miles = serializers.FloatField()
    fuel_stops = FuelStopSerializer(many=True)
    total_fuel_stops = serializers.IntegerField()
    total_gallons = serializers.FloatField()
    total_fuel_cost = serializers.FloatField()
    route_geometry = serializers.ListField(
        help_text="List of [lon, lat] pairs forming the route polyline"
    )