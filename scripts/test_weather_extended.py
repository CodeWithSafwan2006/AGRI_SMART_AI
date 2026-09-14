"""Extended weather API integration tests for AgriSmart.

Tests UV index monitoring, solar advisory, 7-day trend analysis,
growing degree days, and geocoding edge cases.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.weather import (
    geocode_city,
    validate_coordinates,
    fetch_forecast,
    get_weather_summary,
    get_uv_summary,
    solar_advisory,
    weather_advice,
)
from app.forecast_trends import (
    compute_temperature_trend,
    compute_precipitation_outlook,
    compute_growing_degree_days,
)


# ---------------------------------------------------------------------------
# Test utilities
# ---------------------------------------------------------------------------

passed_count = 0
failed_count = 0


def _test(name: str, condition: bool, detail: str = ""):
    global passed_count, failed_count
    status = "✅ PASS" if condition else "❌ FAIL"
    msg = f"  {status} | {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    if condition:
        passed_count += 1
    else:
        failed_count += 1


# ---------------------------------------------------------------------------
# Test: Geocoding
# ---------------------------------------------------------------------------

def test_geocoding():
    """Test geocoding for Indian cities and edge cases."""
    print("\n📍 Geocoding Tests:")

    # Standard Indian cities
    for city in ["Pune", "Delhi", "Nashik", "Ludhiana", "Ahmedabad"]:
        result = geocode_city(city)
        _test(
            f"geocode_city('{city}')",
            result is not None and len(result) == 3,
            f"→ ({result[0]:.2f}, {result[1]:.2f}, {result[2]})" if result else "None",
        )

    # Edge cases
    result = geocode_city("")
    _test("Empty string returns None", result is None)

    result = geocode_city("   ")
    _test("Whitespace-only returns None", result is None)

    result = geocode_city("XyzNonExistentPlace12345")
    _test("Non-existent place returns None", result is None)


# ---------------------------------------------------------------------------
# Test: Coordinate validation
# ---------------------------------------------------------------------------

def test_coordinate_validation():
    """Test GPS coordinate validation bounds."""
    print("\n🌐 Coordinate Validation Tests:")

    _test("Valid Indian coords", validate_coordinates(18.52, 73.86))
    _test("Valid equator", validate_coordinates(0.0, 0.0))
    _test("Valid North Pole", validate_coordinates(90.0, 0.0))
    _test("Valid South Pole", validate_coordinates(-90.0, 0.0))
    _test("Valid date line", validate_coordinates(0.0, 180.0))
    _test("Invalid lat > 90", not validate_coordinates(91.0, 0.0))
    _test("Invalid lat < -90", not validate_coordinates(-91.0, 0.0))
    _test("Invalid lon > 180", not validate_coordinates(0.0, 181.0))
    _test("Invalid lon < -180", not validate_coordinates(0.0, -181.0))


# ---------------------------------------------------------------------------
# Test: Live weather fetch (requires network)
# ---------------------------------------------------------------------------

def test_live_weather_fetch():
    """Test live weather data fetch for Pune."""
    print("\n🌤️ Live Weather Fetch Tests:")

    try:
        # Pune coordinates
        forecast = fetch_forecast(18.5204, 73.8567)

        _test("Forecast returns dict", isinstance(forecast, dict))
        _test("Has 'current' key", "current" in forecast)
        _test("Has 'hourly' key", "hourly" in forecast)
        _test("Has 'daily' key", "daily" in forecast)

        # Weather summary
        summary = get_weather_summary(forecast)
        _test("Summary returns dict", isinstance(summary, dict))
        _test("Has current_temp", "current_temp" in summary)
        _test("Has current_humidity", "current_humidity" in summary)
        _test("Has weather_desc", "weather_desc" in summary)
        _test("Has max_rain_prob_24h", "max_rain_prob_24h" in summary)

        _test(
            "Temperature is reasonable",
            summary["current_temp"] is not None and -20 < summary["current_temp"] < 55,
            f"{summary['current_temp']}°C",
        )

    except Exception as e:
        _test("Weather fetch (network required)", False, str(e))


# ---------------------------------------------------------------------------
# Test: UV index analysis
# ---------------------------------------------------------------------------

def test_uv_index():
    """Test UV index extraction and classification."""
    print("\n☀️ UV Index Tests:")

    try:
        forecast = fetch_forecast(18.5204, 73.8567)
        uv = get_uv_summary(forecast)

        _test("UV summary returns dict", isinstance(uv, dict))
        _test("Has current_uv", "current_uv" in uv)
        _test("Has max_uv_today", "max_uv_today" in uv)
        _test("Has uv_risk_level", "uv_risk_level" in uv)
        _test("Has peak_solar_radiation_wm2", "peak_solar_radiation_wm2" in uv)
        _test("Has recommended_exposure_minutes", "recommended_exposure_minutes" in uv)

        _test(
            "UV risk is valid category",
            uv["uv_risk_level"] in ("Low", "Moderate", "High", "Very High", "Extreme"),
            f"level={uv['uv_risk_level']}",
        )

        # Solar advisory
        tips = solar_advisory(uv, crop="Tomato")
        _test("Solar advisory returns list", isinstance(tips, list))
        _test("Solar advisory has tips", len(tips) > 0, f"{len(tips)} tips")

    except Exception as e:
        _test("UV index analysis (network required)", False, str(e))


# ---------------------------------------------------------------------------
# Test: Weather advice generation
# ---------------------------------------------------------------------------

def test_weather_advice():
    """Test agronomic weather advice with various conditions."""
    print("\n🌾 Weather Advice Tests:")

    # High rain scenario
    tips = weather_advice("Tomato___Late_blight", rain_probability_pct=80, temp_c=25, humidity_pct=85)
    _test("High rain advice generated", len(tips) > 0)
    _test("Rain tip contains precipitation mention", any("precipitation" in t.lower() or "rain" in t.lower() for t in tips))

    # Dry scenario
    tips = weather_advice("Tomato___healthy", rain_probability_pct=5, temp_c=28, humidity_pct=50)
    _test("Dry weather advice generated", len(tips) > 0)

    # Heat stress
    tips = weather_advice("Corn_(maize)___healthy", rain_probability_pct=10, temp_c=40, humidity_pct=30)
    _test("Heat stress tip generated", any("heat" in t.lower() or "temperature" in t.lower() for t in tips))

    # Cold stress
    tips = weather_advice("Potato___healthy", rain_probability_pct=0, temp_c=5, humidity_pct=60)
    _test("Cold stress tip generated", any("cold" in t.lower() or "temperature" in t.lower() or "low" in t.lower() for t in tips))

    # High wind
    tips = weather_advice("healthy", rain_probability_pct=10, temp_c=25, humidity_pct=50, wind_speed=30)
    _test("High wind tip generated", any("wind" in t.lower() for t in tips))


# ---------------------------------------------------------------------------
# Test: Trend analysis with synthetic data
# ---------------------------------------------------------------------------

def test_trend_analysis_synthetic():
    """Test trend computation with synthetic daily data."""
    print("\n📊 Trend Analysis Tests (synthetic data):")

    # Warming trend
    warming_daily = {
        "temperature_2m_max": [28, 29, 30, 31, 32, 33, 34],
        "temperature_2m_min": [18, 19, 20, 21, 22, 23, 24],
        "temperature_2m_mean": [23, 24, 25, 26, 27, 28, 29],
        "time": ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05", "2026-09-06", "2026-09-07"],
    }
    trend = compute_temperature_trend(warming_daily)
    _test("Warming trend detected", trend["trend_direction"] == "warming", f"direction={trend['trend_direction']}")

    # Cooling trend
    cooling_daily = {
        "temperature_2m_max": [34, 33, 32, 31, 30, 29, 28],
        "temperature_2m_min": [24, 23, 22, 21, 20, 19, 18],
        "temperature_2m_mean": [29, 28, 27, 26, 25, 24, 23],
        "time": ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05", "2026-09-06", "2026-09-07"],
    }
    trend = compute_temperature_trend(cooling_daily)
    _test("Cooling trend detected", trend["trend_direction"] == "cooling", f"direction={trend['trend_direction']}")

    # Precipitation outlook
    precip_daily = {
        "precipitation_sum": [0, 0, 5, 15, 0, 0, 2],
        "precipitation_probability_max": [10, 5, 70, 90, 15, 10, 40],
        "time": ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05", "2026-09-06", "2026-09-07"],
    }
    precip = compute_precipitation_outlook(precip_daily)
    _test("Total precipitation calculated", precip["total_precipitation_mm"] == 22.0, f"{precip['total_precipitation_mm']}mm")
    _test("Rainy days counted", precip["rainy_days"] == 2, f"{precip['rainy_days']} days")
    _test("Irrigation recommendation exists", len(precip["irrigation_recommendation"]) > 0)

    # GDD calculation
    gdd_daily = {
        "temperature_2m_max": [30, 32, 28, 35, 31, 29, 33],
        "temperature_2m_min": [20, 22, 18, 25, 21, 19, 23],
        "time": ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05", "2026-09-06", "2026-09-07"],
    }
    gdd = compute_growing_degree_days(gdd_daily, crop="Tomato")
    _test("GDD base temp for Tomato is 10", gdd["base_temp_c"] == 10.0)
    _test("Accumulated GDD > 0", gdd["accumulated_gdd_7d"] > 0, f"{gdd['accumulated_gdd_7d']} GDD")
    _test("Phenology note generated", len(gdd["phenology_note"]) > 0)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main():
    print("\n🌤️ AgriSmart Weather Extended Test Suite")
    print("=" * 50)

    test_geocoding()
    test_coordinate_validation()
    test_live_weather_fetch()
    test_uv_index()
    test_weather_advice()
    test_trend_analysis_synthetic()

    print("\n" + "=" * 50)
    print(f"Results: {passed_count} passed, {failed_count} failed, {passed_count + failed_count} total")
    if failed_count > 0:
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("✅ All tests passed!")


if __name__ == "__main__":
    main()
