"""AgriSmart AI — FastAPI Local Application Server.
Serves REST APIs for AI Model Inference, Weather Intelligence, Chatbot, SQLite Auth, and Static Frontend.
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

# Set UTF-8 encoding on Windows console
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.auth import create_user, init_auth_db, update_user_location, verify_user
from app.chatbot import (
    explain_to_farmer,
    generate_agronomy_advice,
    get_out_of_domain_reply,
    is_agriculture_domain,
    template_explain,
)
from app.precautions import display_name, precaution_for
from app.weather import (
    fetch_forecast,
    geocode_city,
    get_weather_summary,
    validate_coordinates,
    weather_advice,
)
# Load AI model into memory safely
AI_MODEL = None
predict_fn = None
try:
    from model.predict import load_model, predict as p_fn
    predict_fn = p_fn
    AI_MODEL = load_model()
    print("AgriSmart AI Model loaded successfully.")
except Exception as e:
    print(f"Model load notice: {e}")

# Initialize SQLite database
init_auth_db()

app = FastAPI(title="AgriSmart AI", description="Crop Health & Field Intelligence API")

@app.on_event("startup")
def startup_event():
    global AI_MODEL, predict_fn
    if AI_MODEL is None:
        try:
            from model.predict import load_model, predict as p_fn
            predict_fn = p_fn
            AI_MODEL = load_model()
        except Exception:
            pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = ""
    village_city: Optional[str] = "Pune"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    number_of_plots: Optional[int] = 1
    primary_crop: Optional[str] = "Tomato"
    secondary_crop: Optional[str] = "Corn"
    soil_type: Optional[str] = "Loamy"
    language: Optional[str] = "English"


class UpdateLocationRequest(BaseModel):
    username: str
    village_city: str
    latitude: float
    longitude: float


class ChatRequest(BaseModel):
    question: str
    disease_label: Optional[str] = ""
    confidence: Optional[float] = 0.95
    precautions: Optional[str] = ""
    weather_tips: Optional[list[str]] = []
    language: Optional[str] = "English"
    crop: Optional[str] = "Tomato"
    village: Optional[str] = "Pune"
    weather_summary: Optional[dict[str, Any]] = None


# --- API Routes ---

@app.get("/api/health")
def health():
    global AI_MODEL, predict_fn
    if AI_MODEL is None:
        try:
            from model.predict import load_model, predict as p_fn
            predict_fn = p_fn
            AI_MODEL = load_model()
        except Exception:
            pass
    return {"status": "online", "model_loaded": AI_MODEL is not None}


@app.post("/api/auth/signup")
def api_signup(req: SignupRequest):
    city = (req.village_city or "Pune").strip()
    lat = req.latitude
    lon = req.longitude

    # Auto-resolve GPS coordinates via Geocoding if not explicitly supplied
    if lat is None or lon is None or (lat == 18.5204 and lon == 73.8567 and city.lower() != "pune"):
        geo = geocode_city(city)
        if geo:
            lat, lon, _ = geo
        else:
            lat = lat or 18.5204
            lon = lon or 73.8567

    ok, msg = create_user(
        username=req.username,
        password=req.password,
        full_name=req.full_name or req.username.title(),
        village_city=city,
        latitude=lat,
        longitude=lon,
        number_of_plots=req.number_of_plots or 1,
        primary_crop=req.primary_crop or "Tomato",
        secondary_crop=req.secondary_crop or "Corn",
        soil_type=req.soil_type or "Loamy",
        language=req.language or "English",
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    # Auto verify and return user profile
    _, user_profile, _ = verify_user(req.username, req.password)
    return {"success": True, "message": msg, "user": user_profile}


@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    ok, user_profile, msg = verify_user(req.username, req.password)
    if not ok or not user_profile:
        raise HTTPException(status_code=401, detail=msg)
    return {"success": True, "message": msg, "user": user_profile}


@app.post("/api/user/location")
def api_update_location(req: UpdateLocationRequest):
    if not validate_coordinates(req.latitude, req.longitude):
        raise HTTPException(status_code=400, detail="Invalid GPS coordinates.")
    ok, msg = update_user_location(
        username=req.username,
        village_city=req.village_city,
        latitude=req.latitude,
        longitude=req.longitude,
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "village_city": req.village_city, "latitude": req.latitude, "longitude": req.longitude}


@app.get("/api/weather/geocode")
def api_geocode(query: str):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    geo = geocode_city(query.strip())
    if not geo:
        raise HTTPException(status_code=404, detail=f"Location '{query}' not found.")
    lat, lon, label = geo
    return {"latitude": lat, "longitude": lon, "label": label}


@app.get("/api/weather/current")
def api_weather(lat: float, lon: float, disease: Optional[str] = ""):
    if not validate_coordinates(lat, lon):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")
    try:
        raw_data = fetch_forecast(lat, lon)
        summary = get_weather_summary(raw_data)
        tips = weather_advice(
            disease_label=disease or "healthy",
            rain_probability_pct=summary.get("max_rain_prob_24h"),
            temp_c=summary.get("current_temp"),
            humidity_pct=summary.get("current_humidity"),
            wind_speed=summary.get("current_wind"),
        )
        return {
            "summary": summary,
            "raw": raw_data,
            "advice": tips,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Weather fetch error: {exc}")


@app.post("/api/predict")
async def api_predict(
    image: UploadFile = File(...),
    crop: Optional[str] = Form("Tomato"),
    lat: Optional[float] = Form(18.5204),
    lon: Optional[float] = Form(73.8567),
):
    global AI_MODEL, predict_fn
    if AI_MODEL is None or predict_fn is None:
        try:
            from model.predict import load_model, predict as p_fn
            predict_fn = p_fn
            AI_MODEL = load_model()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Model unavailable: {exc}")

    contents = await image.read()
    suffix = Path(image.filename or "leaf.jpg").suffix or ".jpg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        label, conf = predict_fn(tmp_path, model=AI_MODEL)
        disp = display_name(label)
        prec = precaution_for(label)

        # Weather advice derivation
        weather_tips = []
        try:
            fc = fetch_forecast(lat or 18.5204, lon or 73.8567)
            sm = get_weather_summary(fc)
            weather_tips = weather_advice(
                disease_label=label,
                rain_probability_pct=sm.get("max_rain_prob_24h"),
                temp_c=sm.get("current_temp"),
                humidity_pct=sm.get("current_humidity"),
                wind_speed=sm.get("current_wind"),
            )
        except Exception:
            weather_tips = weather_advice(label, None, None)

        return {
            "label": label,
            "display_name": disp,
            "confidence": conf,
            "precautions": prec,
            "weather_tips": weather_tips,
        }
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.post("/api/assistant/chat")
def api_chat(req: ChatRequest):
    user_q = req.question.strip() if req.question else ""
    user_lang = req.language or "English"

    # Strict domain guardrail
    if user_q and not is_agriculture_domain(user_q):
        return {
            "out_of_domain": True,
            "explanation": get_out_of_domain_reply(user_lang)
        }

    advice = generate_agronomy_advice(
        question=user_q,
        disease_display=req.disease_label or f"{req.crop or 'Crop'} foliage",
        confidence=req.confidence or 0.95,
        precautions=req.precautions or "Maintain standard field scouting and balanced fertilization.",
        weather_tips=req.weather_tips or [],
        language=user_lang,
        crop=req.crop or "Tomato",
        village=req.village or "Pune",
        weather_summary=req.weather_summary,
    )

    return {"out_of_domain": False, "explanation": advice}


# --- Static Files & Single Page App Frontend ---
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend index.html building..."}


@app.get("/logo.svg")
@app.get("/favicon.ico")
def serve_logo():
    logo_file = FRONTEND_DIR / "logo.svg"
    if logo_file.exists():
        return FileResponse(logo_file, media_type="image/svg+xml")
    return JSONResponse(status_code=404, content={"detail": "Logo not found"})


if __name__ == "__main__":
    print("Starting AgriSmart Local Web Application on http://127.0.0.1:8000 ...")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
