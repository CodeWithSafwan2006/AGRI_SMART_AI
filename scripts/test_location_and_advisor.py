"""Comprehensive test suite for Location Calibration & AI Agronomy Advisor."""

import sys
import io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.auth import create_user, init_auth_db, update_user_location, verify_user
from app.chatbot import (
    generate_agronomy_advice,
    get_out_of_domain_reply,
    is_agriculture_domain,
)
from app.weather import (
    fetch_forecast,
    geocode_city,
    get_weather_summary,
    validate_coordinates,
)


def run_tests():
    print("==================================================")
    print("Testing Location Geocoding, Forecast & Storage")
    print("==================================================")
    
    # 1. Geocode test
    cities = ["Nashik", "Nagpur, Maharashtra"]
    for city in cities:
        geo = geocode_city(city)
        print(f"Geocoding '{city}': {geo}", flush=True)
        assert geo is not None, f"Geocoding failed for {city}"
        lat, lon, label = geo
        assert validate_coordinates(lat, lon), f"Invalid coordinates for {city}: {lat}, {lon}"

    # 2. Signup with geocoding
    init_auth_db()
    import time
    test_user = f"loc_advisor_{int(time.time())}"
    test_pass = "secure_pass_123"
    n_lat, n_lon = 21.1463, 79.0849

    ok, msg = create_user(
        username=test_user,
        password=test_pass,
        full_name="Ramesh Shinde",
        village_city="Nagpur",
        latitude=n_lat,
        longitude=n_lon,
        primary_crop="Cotton",
        language="Hindi",
    )
    print(f"User signup result: ok={ok}, msg={msg}")
    
    ok_v, user_prof, _ = verify_user(test_user, test_pass)
    assert ok_v and user_prof is not None
    assert user_prof["village_city"] == "Nagpur"
    assert round(user_prof["latitude"], 2) == round(n_lat, 2)
    print(f"Verified profile coordinates: ({user_prof['latitude']}, {user_prof['longitude']})")

    # 3. Update user location
    ok_u, msg_u = update_user_location(test_user, "Nashik", 19.9975, 73.7898)
    assert ok_u, f"Location update failed: {msg_u}"
    _, updated_prof, _ = verify_user(test_user, test_pass)
    assert updated_prof["village_city"] == "Nashik"
    assert abs(updated_prof["latitude"] - 19.9975) < 0.001
    assert abs(updated_prof["longitude"] - 73.7898) < 0.001
    print("Location DB update verified successfully!")

    print("\n==================================================")
    print("Testing AI Agronomy Advisor & Domain Guardrails")
    print("==================================================")

    # In-domain questions
    in_domain_queries = [
        "Should I spray fungicide on my tomato plants with high humidity?",
        "How to prevent leaf blight in humid conditions?",
        "Can I irrigate my crops today?",
        "Is rain expected today in my area?",
        "What dosage of neem oil is safe for aphids?",
        "फसल में कीटनाशक का छिड़काव कब करना चाहिए?",
        "વરસાદમાં પાકનું રક્ષણ કેવી રીતે કરવું?",
    ]
    for q in in_domain_queries:
        is_agri = is_agriculture_domain(q)
        print(f"Domain check for '{q[:45]}...': {is_agri}")
        assert is_agri, f"False negative on agriculture domain check for: {q}"

    # Out-of-domain questions
    out_domain_queries = [
        "What is the capital of France and who won the 2022 World Cup?",
        "Write a Python script to sort a binary tree",
        "Who is the CEO of Tesla?",
    ]
    for q in out_domain_queries:
        is_agri = is_agriculture_domain(q)
        print(f"Domain check for '{q[:45]}...': {is_agri} (Expected False)")
        assert not is_agri, f"False positive on agriculture domain check for: {q}"

    # Agronomy advice generation test
    dummy_summary = {
        "current_temp": 26.5,
        "current_humidity": 82.0,
        "current_wind": 14.2,
        "max_rain_prob_24h": 65.0,
        "weather_desc": "Moderate rain",
    }
    
    advice_en = generate_agronomy_advice(
        question="Can I spray pesticide today?",
        disease_display="Tomato — Early Blight",
        confidence=0.94,
        precautions="Remove infected lower foliage; avoid overhead wetting.",
        weather_tips=["Precipitation probability elevated (65% in 24h). Delay scheduled foliar applications."],
        language="English",
        crop="Tomato",
        village="Nashik",
        weather_summary=dummy_summary,
    )
    print(f"\nGenerated English Advice:\n{advice_en}\n")
    assert "Nashik" in advice_en or "spray" in advice_en.lower() or "precipitation" in advice_en.lower()

    advice_hi = generate_agronomy_advice(
        question="क्या आज छिड़काव करना चाहिए?",
        disease_display="टमाटर — अगेती झुलसा",
        confidence=0.94,
        precautions="संक्रमित पत्तियों को हटाएं और पौधों में हवा का संचार रखें।",
        weather_tips=["बारिश की संभावना अधिक है।"],
        language="Hindi",
        crop="टमाटर",
        village="नासिक",
        weather_summary=dummy_summary,
    )
    print(f"Generated Hindi Advice:\n{advice_hi}\n")
    assert "नासिक" in advice_hi or "बारिश" in advice_hi or "छिड़काव" in advice_hi

    print("\n ALL LOCATION AND AI ADVISOR TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
