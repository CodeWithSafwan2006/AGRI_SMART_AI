"""7-day forecast trend analysis for agricultural planning.

Provides multi-day weather trend metrics including temperature trajectories,
cumulative precipitation forecasts, and growing degree day (GDD) calculations
for crop phenology tracking.
"""

from __future__ import annotations

from typing import Any

import requests

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_7day_forecast(lat: float, lon: float) -> dict[str, Any]:
    """Fetch 7-day daily forecast for trend analysis."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": (
            "temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
            "precipitation_sum,precipitation_probability_max,"
            "wind_speed_10m_max,relative_humidity_2m_mean,"
            "et0_fao_evapotranspiration"
        ),
        "forecast_days": 7,
        "timezone": "auto",
    }
    r = requests.get(FORECAST_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def compute_temperature_trend(daily: dict[str, Any]) -> dict[str, Any]:
    """Analyze 7-day temperature trajectory.

    Returns:
        Dict with trend_direction ('warming', 'cooling', 'stable'),
        avg_max, avg_min, range_spread, and daily_temps list.
    """
    t_max = daily.get("temperature_2m_max") or []
    t_min = daily.get("temperature_2m_min") or []
    t_mean = daily.get("temperature_2m_mean") or []
    dates = daily.get("time") or []

    if not t_max or not t_min:
        return {"trend_direction": "unknown", "daily_temps": []}

    avg_max = sum(t_max) / len(t_max)
    avg_min = sum(t_min) / len(t_min)

    # Trend: compare first half vs second half mean temperatures
    mid = len(t_mean) // 2
    if mid > 0 and t_mean:
        first_half = sum(t_mean[:mid]) / mid
        second_half = sum(t_mean[mid:]) / len(t_mean[mid:])
        delta = second_half - first_half

        if delta > 1.5:
            trend = "warming"
        elif delta < -1.5:
            trend = "cooling"
        else:
            trend = "stable"
    else:
        trend = "stable"
        delta = 0

    daily_temps = []
    for i, date in enumerate(dates):
        daily_temps.append({
            "date": date,
            "max": t_max[i] if i < len(t_max) else None,
            "min": t_min[i] if i < len(t_min) else None,
            "mean": t_mean[i] if i < len(t_mean) else None,
        })

    return {
        "trend_direction": trend,
        "trend_delta_c": round(delta, 1),
        "avg_max_7d": round(avg_max, 1),
        "avg_min_7d": round(avg_min, 1),
        "range_spread": round(avg_max - avg_min, 1),
        "daily_temps": daily_temps,
    }


def compute_precipitation_outlook(daily: dict[str, Any]) -> dict[str, Any]:
    """Analyze 7-day precipitation outlook.

    Returns:
        Dict with total_precipitation_mm, rainy_days, dry_streak,
        max_single_day_mm, and irrigation_recommendation.
    """
    precip = daily.get("precipitation_sum") or []
    precip_prob = daily.get("precipitation_probability_max") or []
    dates = daily.get("time") or []

    total = sum(precip)
    rainy_days = sum(1 for p in precip if p > 1.0)
    dry_days = sum(1 for p in precip if p < 0.5)
    max_day = max(precip) if precip else 0

    # Find longest dry streak
    current_streak = 0
    max_streak = 0
    for p in precip:
        if p < 0.5:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    # Irrigation recommendation
    if total < 5 and dry_days >= 5:
        irrigation = "Critical — schedule supplemental irrigation within 48 hours."
    elif total < 15 and dry_days >= 3:
        irrigation = "Monitor soil moisture; drip irrigation may be needed mid-week."
    elif total > 50:
        irrigation = "Suspend irrigation; risk of waterlogging from heavy forecast precipitation."
    else:
        irrigation = "Adequate rainfall expected. Standard irrigation schedule is sufficient."

    daily_precip = []
    for i, date in enumerate(dates):
        daily_precip.append({
            "date": date,
            "precipitation_mm": precip[i] if i < len(precip) else 0,
            "probability_pct": precip_prob[i] if i < len(precip_prob) else 0,
        })

    return {
        "total_precipitation_mm": round(total, 1),
        "rainy_days": rainy_days,
        "dry_days": dry_days,
        "longest_dry_streak": max_streak,
        "max_single_day_mm": round(max_day, 1),
        "irrigation_recommendation": irrigation,
        "daily_precip": daily_precip,
    }


def compute_growing_degree_days(
    daily: dict[str, Any],
    base_temp: float = 10.0,
    crop: str = "Tomato",
) -> dict[str, Any]:
    """Calculate accumulated Growing Degree Days (GDD) over 7-day forecast.

    GDD = max(0, (T_max + T_min) / 2 - base_temp)

    Args:
        daily: Daily forecast data from Open-Meteo.
        base_temp: Base temperature for GDD calculation (default 10°C for warm-season crops).
        crop: Crop name for context-specific base temperature.

    Returns:
        Dict with accumulated_gdd, daily_gdd list, and phenology_note.
    """
    # Crop-specific base temperatures
    crop_bases = {
        "tomato": 10.0, "potato": 7.0, "corn": 10.0,
        "apple": 7.0, "grape": 10.0, "bell pepper": 10.0,
        "wheat": 5.0, "rice": 10.0,
    }
    base = crop_bases.get(crop.lower(), base_temp)

    t_max = daily.get("temperature_2m_max") or []
    t_min = daily.get("temperature_2m_min") or []
    dates = daily.get("time") or []

    daily_gdd = []
    accumulated = 0.0
    for i, date in enumerate(dates):
        if i < len(t_max) and i < len(t_min):
            gdd = max(0, (t_max[i] + t_min[i]) / 2.0 - base)
        else:
            gdd = 0
        accumulated += gdd
        daily_gdd.append({"date": date, "gdd": round(gdd, 1)})

    # Phenology note
    if accumulated > 100:
        note = f"Strong thermal accumulation ({accumulated:.0f} GDD). Expect rapid growth advancement."
    elif accumulated > 50:
        note = f"Moderate thermal units ({accumulated:.0f} GDD). Normal vegetative progression expected."
    else:
        note = f"Low GDD accumulation ({accumulated:.0f}). Growth may slow; monitor for cold stress."

    return {
        "base_temp_c": base,
        "crop": crop,
        "accumulated_gdd_7d": round(accumulated, 1),
        "daily_gdd": daily_gdd,
        "phenology_note": note,
    }


def get_full_trend_report(lat: float, lon: float, crop: str = "Tomato") -> dict[str, Any]:
    """Generate a comprehensive 7-day trend report combining all analyses.

    Args:
        lat: Latitude of the field.
        lon: Longitude of the field.
        crop: Primary crop for GDD calculation.

    Returns:
        Dict with temperature_trend, precipitation_outlook, growing_degree_days,
        and actionable weekly_summary text.
    """
    forecast = fetch_7day_forecast(lat, lon)
    daily = forecast.get("daily") or {}

    temp_trend = compute_temperature_trend(daily)
    precip_outlook = compute_precipitation_outlook(daily)
    gdd = compute_growing_degree_days(daily, crop=crop)

    # Generate weekly summary text
    summary_parts = []
    summary_parts.append(f"7-Day Outlook: Temperature is {temp_trend['trend_direction']}.")
    summary_parts.append(f"Expected rainfall: {precip_outlook['total_precipitation_mm']}mm across {precip_outlook['rainy_days']} day(s).")
    summary_parts.append(precip_outlook["irrigation_recommendation"])
    summary_parts.append(gdd["phenology_note"])

    return {
        "temperature_trend": temp_trend,
        "precipitation_outlook": precip_outlook,
        "growing_degree_days": gdd,
        "weekly_summary": " ".join(summary_parts),
    }
