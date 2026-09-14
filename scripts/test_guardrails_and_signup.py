"""Test domain guardrails and full farmer signup flow via FastAPI TestClient."""

import sys
import io
from pathlib import Path

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_api():
    print("[1/3] Testing Health...")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"Health: {r.json()}")

    print("\n[2/3] Testing Out-Of-Domain Chat & Advisor...")
    # Out of domain question
    r = client.post("/api/assistant/chat", json={
        "question": "What is the capital of France and who won the World Cup?",
        "language": "English"
    })
    res = r.json()
    print("Out-of-domain result:", res)
    assert res["out_of_domain"] is True, "Domain guardrail failed for non-agri question"

    # In-domain question
    r = client.post("/api/assistant/chat", json={
        "question": "Should I spray fungicide on my tomato plants with high humidity?",
        "crop": "Tomato",
        "village": "Pune",
        "language": "English"
    })
    res = r.json()
    print("\nIn-domain result:", res)
    assert res["out_of_domain"] is False, "Domain guardrail failed for valid agri question"
    assert len(res["explanation"]) > 15

    print("\n[3/3] Testing Full Farmer Signup with Plots & Crops...")
    import time
    uname = f"kisan_vijay_{int(time.time())}"
    r = client.post("/api/auth/signup", json={
        "username": uname,
        "password": "pass_farmer_123",
        "full_name": "Vijay Shinde",
        "village_city": "Nagpur",
        "number_of_plots": 4,
        "primary_crop": "Cotton",
        "secondary_crop": "Soybean",
        "soil_type": "Black Cotton",
        "language": "Marathi"
    })
    signup_res = r.json()
    print("Signup result:", signup_res)
    assert r.status_code == 200, f"Unexpected signup response: {signup_res}"
    assert signup_res["user"]["village_city"] == "Nagpur"
    assert round(signup_res["user"]["latitude"], 1) == 21.1

    print("\n ALL GUARDRAIL & ONBOARDING FASTAPI TESTS PASSED!")

if __name__ == "__main__":
    test_api()
