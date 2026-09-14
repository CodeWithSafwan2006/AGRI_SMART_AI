"""Open-Meteo weather intelligence: geocoding, manual coordinate input, real-time metrics, and agricultural advisory."""

from __future__ import annotations

from typing import Any
import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Clean WMO descriptions (minimalist, no emojis)
WMO_DESCRIPTIONS = {
    0: ("Clear sky", "Optimal conditions for scouting and canopy management."),
    1: ("Mainly clear", "Favorable conditions for foliar application or harvesting."),
    2: ("Partly cloudy", "Mild conditions with intermittent solar exposure."),
    3: ("Overcast", "Low solar irradiance; steady leaf surface moisture."),
    45: ("Fog", "High boundary-layer moisture; monitor for fungal progression."),
    48: ("Rime fog", "Extended surface dampness across vegetation."),
    51: ("Light drizzle", "Superficial moisture on crop canopy."),
    53: ("Moderate drizzle", "Postpone foliar applications until dry."),
    55: ("Dense drizzle", "Suspend spray operations and soil cultivation."),
    61: ("Slight rain", "Delay irrigation; active canopy wetness."),
    63: ("Moderate rain", "Halt chemical and nutrient applications."),
    65: ("Heavy rain", "Risk of nutrient leaching and surface runoff."),
    71: ("Slight snow", "Cold stress alert."),
    80: ("Rain showers", "Variable precipitation patterns expected."),
    95: ("Thunderstorm", "Severe weather; protect vulnerable seedlings."),
}


def geocode_city(city: str, country: str = "") -> tuple[float, float, str] | None:
    """Geocode a city, village, or district name via Open-Meteo Geocoding API."""
    clean = city.strip()
    if not clean:
        return None

    search_terms = [clean]
    if "," in clean:
        primary_part = clean.split(",")[0].strip()
        if primary_part:
            search_terms.append(primary_part)

    for term in search_terms:
        params = {"name": term, "count": 5, "language": "en", "format": "json"}
        if country:
            params["country"] = country
        try:
            r = requests.get(GEOCODE_URL, params=params, timeout=12)
            r.raise_for_status()
            results = r.json().get("results") or []
            if results:
                hit = results[0]
                name = hit.get("name", term)
                admin1 = hit.get("admin1", "")
                country_name = hit.get("country", "")
                parts = [p for p in [name, admin1, country_name] if p]
                label = ", ".join(parts)
                return float(hit["latitude"]), float(hit["longitude"]), label
        except Exception:
            continue

    return None


def validate_coordinates(lat: float, lon: float) -> bool:
    """Check if latitude and longitude values are within standard GPS bounds."""
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def fetch_forecast(lat: float, lon: float) -> dict[str, Any]:
    """Fetch live weather and hourly/daily forecast for specific GPS coordinates."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "hourly": "temperature_2m,precipitation_probability,relative_humidity_2m,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum",
        "forecast_days": 3,
        "timezone": "auto",
    }
    r = requests.get(FORECAST_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def get_weather_summary(forecast: dict[str, Any]) -> dict[str, Any]:
    """Extract structured real-time and 24h summary metrics from forecast data."""
    current = forecast.get("current") or {}
    hourly = forecast.get("hourly") or {}

    curr_temp = current.get("temperature_2m")
    curr_humidity = current.get("relative_humidity_2m")
    curr_wind = current.get("wind_speed_10m")
    curr_code = current.get("weather_code", 0)

    weather_desc, weather_note = WMO_DESCRIPTIONS.get(
        curr_code, ("Partly cloudy", "Stable agricultural weather conditions.")
    )

    temps_24h = (hourly.get("temperature_2m") or [])[:24]
    rain_p_24h = (hourly.get("precipitation_probability") or [])[:24]
    humid_24h = (hourly.get("relative_humidity_2m") or [])[:24]
    wind_24h = (hourly.get("wind_speed_10m") or [])[:24]

    avg_temp = (sum(temps_24h) / len(temps_24h)) if temps_24h else curr_temp
    max_rain_prob = max(rain_p_24h) if rain_p_24h else 0
    avg_humidity = (sum(humid_24h) / len(humid_24h)) if humid_24h else curr_humidity
    max_wind = max(wind_24h) if wind_24h else curr_wind

    return {
        "current_temp": curr_temp,
        "current_humidity": curr_humidity,
        "current_wind": curr_wind,
        "weather_desc": weather_desc,
        "weather_note": weather_note,
        "avg_temp_24h": avg_temp,
        "max_rain_prob_24h": float(max_rain_prob),
        "avg_humidity_24h": avg_humidity,
        "max_wind_24h": max_wind,
    }


def weather_advice(
    disease_label: str,
    rain_probability_pct: float | None,
    temp_c: float | None,
    humidity_pct: float | None = None,
    wind_speed: float | None = None,
) -> list[str]:
    """Generate agronomic recommendations based on weather and disease status."""
    tips: list[str] = []
    d_lower = disease_label.lower()

    if rain_probability_pct is not None and rain_probability_pct >= 50:
        tips.append(
            f"Precipitation probability elevated ({rain_probability_pct:.0f}% in 24h). Delay scheduled foliar applications to prevent runoff wash-off."
        )
    elif rain_probability_pct is not None and rain_probability_pct < 20:
        tips.append("Dry canopy conditions expected. Favorable window for necessary preventative treatments or pruning.")

    if (
        (humidity_pct is not None and humidity_pct > 75)
        or ("blight" in d_lower or "mold" in d_lower or "spot" in d_lower or "rust" in d_lower)
    ):
        if temp_c is not None and 18 <= temp_c <= 32:
            tips.append(
                "Elevated relative humidity within 18–32°C range creates a favorable infection window for foliar pathogens. Ensure canopy ventilation."
            )

    if temp_c is not None and temp_c > 35:
        tips.append(
            f"Canopy temperature ({temp_c:.1f}°C) may induce heat stress. Maintain adequate root zone moisture."
        )
    elif temp_c is not None and temp_c < 12:
        tips.append(
            f"Low ambient temperature ({temp_c:.1f}°C) slows metabolic rate. Monitor for cold vulnerability."
        )

    if wind_speed is not None and wind_speed > 20:
        tips.append(
            f"Wind velocity ({wind_speed:.1f} km/h) exceeds safe threshold for spray drift. Suspend mechanical spraying operations."
        )

    if not tips:
        tips.append("Atmospheric parameters are within baseline ranges. Proceed with standard crop maintenance.")

    return tips
