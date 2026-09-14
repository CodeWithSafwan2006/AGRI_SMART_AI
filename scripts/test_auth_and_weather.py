"""Automated verification test for auth and weather modules."""

import sys
import io
from pathlib import Path

# Fix windows console unicode printing
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.auth import create_user, verify_user, init_auth_db
from app.weather import geocode_city, validate_coordinates, fetch_forecast, get_weather_summary, weather_advice


def test_auth():
    print("[1/4] Testing Auth DB & User Flow...")
    init_auth_db()
    
    # Test Signup
    import time
    test_user = f"test_farmer_{int(time.time())}"
    test_pass = "secure_pass_123"
    ok, msg = create_user(
        username=test_user,
        password=test_pass,
        full_name="Kisan Ramesh",
        village_city="Nashik",
        latitude=19.9975,
        longitude=73.7898,
        crop_preference="Grape",
        language="Hindi",
    )
    print(f"Create user result: ok={ok}, msg={msg}")
    assert ok or "already taken" in msg, f"Failed create user: {msg}"

    # Test Valid Login
    ok, user_data, msg = verify_user(test_user, test_pass)
    print(f"Login valid result: ok={ok}, user={user_data.get('username') if user_data else None}, msg={msg}")
    assert ok and user_data is not None, "Login verification failed"
    assert user_data["username"] == test_user
    assert user_data["crop_preference"] == "Grape"

    # Test Invalid Login
    ok, user_data, msg = verify_user(test_user, "wrong_password_xyz")
    print(f"Login invalid pass result: ok={ok}, msg={msg}")
    assert not ok and user_data is None, "Failed: invalid password was accepted!"

    print(" Auth tests passed successfully!")


def test_weather():
    print("\n[2/4] Testing Geocoding...")
    geo = geocode_city("Nashik")
    print(f"Geocoded 'Nashik': {geo}")
    assert geo is not None, "Geocoding failed for Nashik"
    lat, lon, label = geo
    assert validate_coordinates(lat, lon), "Invalid coordinates from geocode"

    print("\n[3/4] Testing Forecast & Live Weather...")
    fc = fetch_forecast(lat, lon)
    assert "current" in fc or "hourly" in fc, "Malformed forecast response"
    summary = get_weather_summary(fc)
    print(f"Weather summary: {summary}")
    assert summary["current_temp"] is not None
    assert summary["weather_desc"] is not None

    print("\n[4/4] Testing Agronomic Advice...")
    advice = weather_advice(
        disease_label="Tomato___Late_blight",
        rain_probability_pct=65.0,
        temp_c=24.5,
        humidity_pct=85.0,
        wind_speed=12.0,
    )
    print("Generated advice:")
    for a in advice:
        print(f" - {a}")
    assert len(advice) > 0

    print("\n ALL AUTH & WEATHER INTEGRATION TESTS PASSED!")


if __name__ == "__main__":
    test_auth()
    test_weather()
