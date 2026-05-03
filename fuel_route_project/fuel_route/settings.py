from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-fuel-route-assessment-key-change-in-prod'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'route_planner',
    'django.contrib.auth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'fuel_route.urls'
WSGI_APPLICATION = 'fuel_route.wsgi.application'

DATABASES = {}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_TZ = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Paths & constants
FUEL_PRICES_CSV = os.path.join(BASE_DIR, 'fuel_prices.csv')
VEHICLE_MAX_RANGE_MILES = 500
VEHICLE_MPG = 10

# Free APIs — no key needed
OSRM_BASE_URL = 'http://router.project-osrm.org'
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'