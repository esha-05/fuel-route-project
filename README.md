# ⛽ Fuel Route Planner API

A Django REST API that calculates the optimal fuel stops along a driving route within the USA, based on real fuel prices. Given a start and finish location, it returns the cheapest gas stations to stop at, the total fuel cost, and the full map route geometry.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Server](#running-the-server)
- [API Usage](#api-usage)
- [How It Works](#how-it-works)
- [External APIs Used](#external-apis-used)
- [Vehicle Assumptions](#vehicle-assumptions)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

- Accepts any two US city/address locations as input
- Returns the full driving route geometry (polyline coordinates for map rendering)
- Calculates optimal fuel stop locations based on **cheapest price nearby**
- Handles multiple fuel stops for long routes (vehicle max range: 500 miles)
- Returns total gallons used and total money spent on fuel
- Uses **free APIs only** — no API keys required
- Maximum **3 external API calls** per request (2 geocoding + 1 routing)
- Station geocoding is **cached to disk** — fast after first run

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| Framework | Django 6.x + Django REST Framework |
| Geocoding | Nominatim (OpenStreetMap) — free, no key |
| Routing | OSRM (Open Source Routing Machine) — free, no key |
| City Coordinates | SimpleMaps US Cities CSV — free download |
| Fuel Price Data | Provided CSV (8,151 stations) |
| Language | Python 3.10+ |

---

## 📁 Project Structure

```
fuel_route_project/
│
├── manage.py
├── requirements.txt
├── fuel_prices.csv          ← fuel station price data (provided)
├── uscities.csv             ← US cities lat/lon data (download separately)
├── geocode_cache.json       ← auto-generated cache (created on first run)
│
├── fuel_route/              ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── route_planner/           ← Django app
    ├── apps.py              ← startup pre-warming
    ├── urls.py              ← API route definitions
    ├── views.py             ← main API endpoint logic
    ├── serializers.py       ← input validation & response formatting
    ├── geocoder.py          ← converts city names to lat/lon
    ├── osrm_client.py       ← single OSRM routing API call
    ├── fuel_data.py         ← loads CSV, finds cheapest nearby station
    └── route_optimizer.py   ← greedy fuel stop algorithm
```

---

## ✅ Prerequisites

- Python 3.10 or higher
- pip
- Internet connection (for geocoding and routing API calls)

Check your Python version:
```bash
python --version
```

---

## 🚀 Installation & Setup

### Step 1 — Clone or download the project

```bash
cd your-projects-folder
# unzip the project or clone it
```

### Step 2 — Create and activate a virtual environment

```bash
# Create
python -m venv venv

# Activate on Mac/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Download the US Cities dataset

This file provides lat/lon coordinates for US cities (used to locate fuel stations offline).

1. Go to: [https://simplemaps.com/data/us-cities](https://simplemaps.com/data/us-cities)
2. Click **"Download Basic (Free)"**
3. Extract the zip file
4. Copy `uscities.csv` into your project root (next to `manage.py`)

### Step 5 — Add the fuel prices CSV

Make sure `fuel_prices.csv` is in the project root (next to `manage.py`).

Your project root should look like this:
```
fuel_route_project/
├── manage.py
├── fuel_prices.csv      ✅
├── uscities.csv         ✅
├── requirements.txt
├── fuel_route/
└── route_planner/
```

---

## ▶️ Running the Server

```bash
python manage.py runserver
```

Expected output:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL+C.
```

> ⚠️ **First run note:** On the very first request, the server will geocode fuel station city/state pairs from the CSV. This may take a few minutes. After that, results are cached in `geocode_cache.json` and all future requests are fast (2–5 seconds).

---

## 📡 API Usage

### Endpoint

```
POST /api/route/
Content-Type: application/json
```

### Request Body

```json
{
    "start": "Chicago, IL",
    "finish": "Dallas, TX"
}
```

| Field | Type | Description |
|---|---|---|
| `start` | string | Starting location within the USA |
| `finish` | string | Destination location within the USA |

### Example — Using Postman

1. Open Postman
2. Set method to **POST**
3. URL: `http://127.0.0.1:8000/api/route/`
4. Go to **Body** → select **raw** → select **JSON**
5. Paste the request body above
6. Click **Send**

### Example — Using curl

```bash
curl -X POST http://127.0.0.1:8000/api/route/ \
  -H "Content-Type: application/json" \
  -d '{"start": "Chicago, IL", "finish": "Dallas, TX"}'
```

### Example — Using Python

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/api/route/",
    json={"start": "Chicago, IL", "finish": "Dallas, TX"}
)
print(response.json())
```

---

## 📤 Response Format

```json
{
    "start": "Chicago, IL",
    "finish": "Dallas, TX",
    "start_coords": {
        "lat": 41.85,
        "lon": -87.65
    },
    "finish_coords": {
        "lat": 32.77,
        "lon": -96.79
    },
    "total_distance_miles": 964.19,
    "total_fuel_stops": 2,
    "total_gallons": 96.42,
    "total_fuel_cost": 298.45,
    "fuel_stops": [
        {
            "stop_number": 1,
            "station_name": "PILOT TRAVEL CENTER #492",
            "city": "Springfield",
            "state": "IL",
            "lat": 39.80,
            "lon": -89.65,
            "price_per_gallon": 3.05,
            "gallons_purchased": 40.0,
            "cost": 122.00,
            "miles_from_start": 400.0
        },
        {
            "stop_number": 2,
            "station_name": "LOVES TRAVEL STOP #287",
            "city": "Ardmore",
            "state": "OK",
            "lat": 34.17,
            "lon": -97.13,
            "price_per_gallon": 2.98,
            "gallons_purchased": 36.0,
            "cost": 107.28,
            "miles_from_start": 760.0
        }
    ],
    "route_geometry": [
        [-87.534067, 41.691563],
        [-87.534067, 41.691378],
        "... hundreds of [lon, lat] coordinate pairs ..."
    ]
}
```

### Response Fields Explained

| Field | Description |
|---|---|
| `start` / `finish` | Original input strings |
| `start_coords` / `finish_coords` | Geocoded lat/lon for start and finish |
| `total_distance_miles` | Total driving distance |
| `total_fuel_stops` | Number of fuel stops needed |
| `total_gallons` | Total gallons of fuel used for the trip |
| `total_fuel_cost` | Total money spent on fuel in USD |
| `fuel_stops` | Array of stop details (see below) |
| `route_geometry` | Array of `[longitude, latitude]` pairs — the full driving route polyline for rendering on a map |

### Fuel Stop Fields

| Field | Description |
|---|---|
| `stop_number` | Order of the stop (1, 2, 3...) |
| `station_name` | Name of the fuel station |
| `city` / `state` | Location of the station |
| `lat` / `lon` | GPS coordinates of the station |
| `price_per_gallon` | Fuel price at this station |
| `gallons_purchased` | How many gallons to fill up here |
| `cost` | Total cost at this stop |
| `miles_from_start` | How far into the trip this stop is |

### What is `route_geometry`?

The `route_geometry` is a list of `[longitude, latitude]` coordinate pairs that trace the exact driving path from start to finish. Connect all these points on a map and you get the blue route line. You can render this using:

- **Leaflet.js** (open source)
- **Mapbox GL JS**
- **Google Maps JS API**
- **Folium** (Python)

---

## ⚙️ How It Works

```
1. Validate input (start + finish city names)
         ↓
2. Geocode both locations in parallel
   → Converts "Chicago, IL" to (41.85, -87.65)
   → 2 API calls to Nominatim
         ↓
3. Get driving route from OSRM
   → 1 API call returns full route polyline + total distance
         ↓
4. Walk the route, find cheapest fuel stops
   → Pure in-memory computation, no more API calls
   → Triggers every ~400 miles (80% of 500 mile tank)
   → Searches nearby stations within 50 mile radius
   → Picks cheapest price as the winner
         ↓
5. Return full JSON response
```

**Total external API calls per request: maximum 3**
- 2 × Nominatim geocoding (start + finish, run in parallel)
- 1 × OSRM routing

---

## 🌐 External APIs Used

### 1. Nominatim (OpenStreetMap Geocoding)
- **URL:** `https://nominatim.openstreetmap.org/search`
- **Cost:** Free, no API key required
- **Rate limit:** 1 request/second (handled automatically)
- **Usage:** Converts city names to lat/lon coordinates

### 2. OSRM (Open Source Routing Machine)
- **URL:** `http://router.project-osrm.org`
- **Cost:** Free, no API key required
- **Usage:** Returns full driving route geometry and distance in a single call

---

## 🚗 Vehicle Assumptions

| Setting | Value |
|---|---|
| Max range per tank | 500 miles |
| Fuel economy | 10 miles per gallon |
| Fuel trigger threshold | 400 miles (refuel at 80% of range) |
| Station search radius | 50 miles from route |

These can be changed in `fuel_route/settings.py`:
```python
VEHICLE_MAX_RANGE_MILES = 500
VEHICLE_MPG = 10
```

---

## 🔧 Troubleshooting

### `No module named 'pandas'`
```bash
# Make sure venv is activated, then:
pip install -r requirements.txt
```

### `fuel_prices.csv not found`
Place `fuel_prices.csv` next to `manage.py` in the project root.

### `uscities.csv not found`
Download from [simplemaps.com/data/us-cities](https://simplemaps.com/data/us-cities) and place next to `manage.py`.

### `fuel_stops` is empty
This means the US cities file is missing or the station geocoding hasn't completed yet. Make sure `uscities.csv` is in place and restart the server.

### Port 8000 already in use
```bash
python manage.py runserver 8001
# Then use http://127.0.0.1:8001/api/route/
```

### First request is very slow
This is normal — the server is geocoding station locations on first run. Wait for it to complete. Subsequent requests will be fast (2–5 seconds).

---

## 📦 Requirements

```
Django>=6.0
djangorestframework>=3.15
pandas>=2.0
requests>=2.31
```
