# AgriSmart AI — API Reference

Complete REST API documentation for the AgriSmart crop health and field intelligence platform.

**Base URL:** `http://127.0.0.1:8000`

---

## Table of Contents

- [Health Check](#health-check)
- [Authentication](#authentication)
  - [Sign Up](#sign-up)
  - [Login](#login)
  - [Update Location](#update-location)
- [Weather Intelligence](#weather-intelligence)
  - [Geocode City](#geocode-city)
  - [Current Weather](#current-weather)
- [AI Prediction](#ai-prediction)
  - [Predict Disease](#predict-disease)
- [Field Assistant](#field-assistant)
  - [Chat](#chat)

---

## Health Check

### `GET /api/health`

Check API server status and model availability.

**Response:**
```json
{
  "status": "online",
  "model_loaded": true
}
```

---

## Authentication

### Sign Up

#### `POST /api/auth/signup`

Create a new farmer profile with auto-geocoded location.

**Request Body:**
```json
{
  "username": "satish_patel",
  "password": "SecurePass123!",
  "full_name": "Satish Patel",
  "village_city": "Nashik",
  "latitude": null,
  "longitude": null,
  "number_of_plots": 2,
  "primary_crop": "Grape",
  "secondary_crop": "Tomato",
  "soil_type": "Black Cotton",
  "language": "Hindi"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Account created successfully.",
  "user": {
    "username": "satish_patel",
    "full_name": "Satish Patel",
    "village_city": "Nashik",
    "latitude": 19.9975,
    "longitude": 73.7898,
    "crop_preference": "Grape",
    "language": "Hindi"
  }
}
```

**Error (400):**
```json
{
  "detail": "Username already exists."
}
```

> **Note:** If `latitude`/`longitude` are null, the server auto-geocodes the `village_city` via Open-Meteo.

---

### Login

#### `POST /api/auth/login`

Authenticate a farmer and retrieve their profile.

**Request Body:**
```json
{
  "username": "satish_patel",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Welcome back, Satish Patel!",
  "user": {
    "username": "satish_patel",
    "full_name": "Satish Patel",
    "village_city": "Nashik",
    "latitude": 19.9975,
    "longitude": 73.7898,
    "crop_preference": "Grape",
    "language": "Hindi"
  }
}
```

**Error (401):**
```json
{
  "detail": "Invalid username or password."
}
```

---

### Update Location

#### `POST /api/user/location`

Update a farmer's registered GPS location and village.

**Request Body:**
```json
{
  "username": "satish_patel",
  "village_city": "Pune",
  "latitude": 18.5204,
  "longitude": 73.8567
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Location updated.",
  "village_city": "Pune",
  "latitude": 18.5204,
  "longitude": 73.8567
}
```

---

## Weather Intelligence

### Geocode City

#### `GET /api/weather/geocode?query={city_name}`

Resolve a village, city, or district name to GPS coordinates.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | City, village, or district name |

**Example:** `GET /api/weather/geocode?query=Ludhiana`

**Response (200):**
```json
{
  "latitude": 30.9010,
  "longitude": 75.8573,
  "label": "Ludhiana, Punjab, India"
}
```

**Error (404):**
```json
{
  "detail": "Location 'xyz' not found."
}
```

---

### Current Weather

#### `GET /api/weather/current?lat={lat}&lon={lon}&disease={label}`

Get real-time weather data, 24h summary, and agronomic advice.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | Yes | Latitude (-90 to 90) |
| `lon` | float | Yes | Longitude (-180 to 180) |
| `disease` | string | No | Current disease label for contextualized advice |

**Example:** `GET /api/weather/current?lat=18.52&lon=73.86&disease=Tomato___Late_blight`

**Response (200):**
```json
{
  "summary": {
    "current_temp": 28.5,
    "current_humidity": 72,
    "current_wind": 8.3,
    "weather_desc": "Partly cloudy",
    "weather_note": "Mild conditions with intermittent solar exposure.",
    "avg_temp_24h": 27.8,
    "max_rain_prob_24h": 35.0,
    "avg_humidity_24h": 68.5,
    "max_wind_24h": 15.2
  },
  "raw": { "...full Open-Meteo response..." },
  "advice": [
    "Elevated relative humidity within 18–32°C range creates a favorable infection window for foliar pathogens. Ensure canopy ventilation."
  ]
}
```

---

## AI Prediction

### Predict Disease

#### `POST /api/predict`

Upload a leaf photograph for AI-powered disease classification.

**Content-Type:** `multipart/form-data`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | file | Yes | Leaf photo (JPG, JPEG, or PNG) |
| `crop` | string | No | Crop type (default: "Tomato") |
| `lat` | float | No | Field latitude for weather context |
| `lon` | float | No | Field longitude for weather context |

**Example (cURL):**
```bash
curl -X POST http://127.0.0.1:8000/api/predict \
  -F "image=@leaf_sample.jpg" \
  -F "crop=Tomato" \
  -F "lat=18.52" \
  -F "lon=73.86"
```

**Response (200):**
```json
{
  "label": "Tomato___Late_blight",
  "display_name": "Tomato — Late blight",
  "confidence": 0.934,
  "precautions": "Remove and destroy affected plants; do not compost; reduce humidity and overhead irrigation.",
  "weather_tips": [
    "Elevated relative humidity within 18–32°C range creates a favorable infection window for foliar pathogens."
  ]
}
```

**Supported Classes (18):**
| Crop | Diseases |
|------|----------|
| Tomato | Early Blight, Late Blight, Leaf Mold, Bacterial Spot, Healthy |
| Potato | Early Blight, Late Blight, Healthy |
| Corn | Common Rust, Gray Leaf Spot, Healthy |
| Apple | Apple Scab, Black Rot, Healthy |
| Grape | Black Rot, Healthy |
| Bell Pepper | Bacterial Spot, Healthy |

---

## Field Assistant

### Chat

#### `POST /api/assistant/chat`

Ask the multilingual AI field assistant for grounded agronomy advice.

**Request Body:**
```json
{
  "question": "Should I spray fungicide today?",
  "disease_label": "Tomato — Late blight",
  "confidence": 0.93,
  "precautions": "Remove and destroy affected plants.",
  "weather_tips": ["High humidity favors blight spread."],
  "language": "English",
  "crop": "Tomato",
  "village": "Nashik",
  "weather_summary": {
    "current_temp": 26.5,
    "current_humidity": 82,
    "current_wind": 6.0,
    "max_rain_prob_24h": 70
  }
}
```

**Response (200) — In-domain:**
```json
{
  "out_of_domain": false,
  "explanation": "Agronomic Assessment for Tomato at Nashik Station: Precipitation probability is elevated (70% in 24h). Postpone foliar spray applications..."
}
```

**Response (200) — Out-of-domain:**
```json
{
  "out_of_domain": true,
  "explanation": "I'm AgriSmart, an agricultural field advisor. I can only help with crop health, weather, and farming questions."
}
```

**Supported Languages:** English, Hindi (हिन्दी), Gujarati (ગુજરાતી), Marathi (मराठी)

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Human-readable error message."
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request — Invalid input parameters |
| 401 | Unauthorized — Invalid credentials |
| 404 | Not Found — Resource not found |
| 429 | Too Many Requests — Rate limit exceeded |
| 500 | Internal Server Error — Server-side failure |

---

## Rate Limiting

API requests are rate-limited to **60 requests per minute** per IP address.

**Rate limit headers in responses:**
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `Retry-After`: Seconds until rate limit resets (on 429 responses)

---

*Generated for AgriSmart AI v1.0 — Smart India Hackathon 2026*
