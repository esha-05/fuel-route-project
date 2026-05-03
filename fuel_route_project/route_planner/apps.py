from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class RoutePlannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'route_planner'

    def ready(self):
        """
        Pre-warm the fuel station data on server startup.
        This geocodes all city/state pairs once and caches to disk,
        so the first API request isn't slow.
        """
        import threading

        def _prewarm():
            try:
                from .fuel_data import get_stations
                stations = get_stations()
                logger.info(f"[Startup] Fuel data ready: {len(stations)} stations loaded.")
            except Exception as e:
                logger.error(f"[Startup] Failed to prewarm fuel data: {e}")

        # Run in background thread so server starts immediately
        t = threading.Thread(target=_prewarm, daemon=True)
        t.start()