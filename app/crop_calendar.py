"""Crop calendar and seasonal planting guide for Indian agriculture.

Provides season-aware planting recommendations, crop rotation schedules,
and growth stage timelines aligned with Indian Kharif/Rabi/Zaid seasons.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


# ---------------------------------------------------------------------------
# Indian agricultural seasons
# ---------------------------------------------------------------------------

SEASONS = {
    "Kharif": {
        "months": [6, 7, 8, 9, 10],
        "label": "Kharif (Monsoon)",
        "description": "Southwest monsoon season. High rainfall, warm temperatures.",
        "typical_crops": ["Rice", "Cotton", "Corn", "Soybean", "Groundnut", "Sugarcane"],
    },
    "Rabi": {
        "months": [11, 12, 1, 2, 3],
        "label": "Rabi (Winter)",
        "description": "Post-monsoon winter season. Cool, dry conditions.",
        "typical_crops": ["Wheat", "Mustard", "Chickpea", "Potato", "Barley", "Linseed"],
    },
    "Zaid": {
        "months": [3, 4, 5, 6],
        "label": "Zaid (Summer)",
        "description": "Hot dry summer between Rabi and Kharif. Irrigation-dependent.",
        "typical_crops": ["Watermelon", "Muskmelon", "Cucumber", "Moong", "Sunflower"],
    },
}


def get_current_season(month: int | None = None) -> dict[str, Any]:
    """Determine the current Indian agricultural season.

    Args:
        month: Month number (1-12). Uses current month if None.

    Returns:
        Dict with season name, label, description, and typical crops.
    """
    if month is None:
        month = datetime.now().month

    for season_name, info in SEASONS.items():
        if month in info["months"]:
            return {
                "season": season_name,
                "label": info["label"],
                "description": info["description"],
                "typical_crops": info["typical_crops"],
                "current_month": month,
            }

    return {
        "season": "Transition",
        "label": "Seasonal Transition",
        "description": "Between agricultural seasons.",
        "typical_crops": [],
        "current_month": month,
    }


# ---------------------------------------------------------------------------
# Crop-specific planting calendars
# ---------------------------------------------------------------------------

CROP_CALENDAR: dict[str, dict[str, Any]] = {
    "Tomato": {
        "optimal_sowing_months": [6, 7, 9, 10, 1, 2],
        "nursery_days": 25,
        "transplant_to_harvest_days": 75,
        "season": "Kharif / Rabi",
        "growth_stages": [
            {"stage": "Nursery", "duration_days": 25, "description": "Sow seeds in nursery beds with partial shade."},
            {"stage": "Transplanting", "duration_days": 7, "description": "Transplant seedlings at 4-5 leaf stage."},
            {"stage": "Vegetative", "duration_days": 30, "description": "Stake plants; apply balanced NPK fertilizer."},
            {"stage": "Flowering", "duration_days": 15, "description": "Monitor for blossom-end rot; ensure calcium availability."},
            {"stage": "Fruiting", "duration_days": 25, "description": "Reduce nitrogen; monitor for late blight in humid spells."},
            {"stage": "Harvest", "duration_days": 14, "description": "Pick at 75% color break for market; full red for processing."},
        ],
        "spacing_cm": "60 × 45",
        "water_requirement_mm": "500-600",
        "key_diseases": ["Early Blight", "Late Blight", "Leaf Mold", "Bacterial Spot"],
    },
    "Potato": {
        "optimal_sowing_months": [10, 11, 12, 1],
        "seed_to_harvest_days": 90,
        "season": "Rabi",
        "growth_stages": [
            {"stage": "Planting", "duration_days": 1, "description": "Plant seed tubers 5-8 cm deep in ridges."},
            {"stage": "Emergence", "duration_days": 15, "description": "First shoots appear; maintain soil moisture."},
            {"stage": "Vegetative", "duration_days": 25, "description": "Hill up soil around stems; apply earthing."},
            {"stage": "Tuber Initiation", "duration_days": 15, "description": "Reduce nitrogen; tubers begin forming."},
            {"stage": "Tuber Bulking", "duration_days": 25, "description": "Critical irrigation period; monitor for blight."},
            {"stage": "Maturation", "duration_days": 10, "description": "Desiccate foliage; prepare for harvest."},
        ],
        "spacing_cm": "60 × 20",
        "water_requirement_mm": "400-500",
        "key_diseases": ["Early Blight", "Late Blight"],
    },
    "Corn": {
        "optimal_sowing_months": [6, 7, 1, 2],
        "seed_to_harvest_days": 100,
        "season": "Kharif / Rabi",
        "growth_stages": [
            {"stage": "Sowing", "duration_days": 1, "description": "Direct seed at 5 cm depth."},
            {"stage": "Emergence", "duration_days": 7, "description": "Seeds germinate; thin to final spacing."},
            {"stage": "Vegetative (V-stages)", "duration_days": 40, "description": "Rapid leaf development; apply nitrogen top-dress at V6."},
            {"stage": "Tasseling", "duration_days": 10, "description": "Critical water demand; avoid moisture stress."},
            {"stage": "Silking & Pollination", "duration_days": 15, "description": "Kernel set period; monitor for fall armyworm."},
            {"stage": "Grain Fill", "duration_days": 20, "description": "Dry-down phase; scout for common rust."},
            {"stage": "Harvest", "duration_days": 7, "description": "Harvest at 20-25% grain moisture."},
        ],
        "spacing_cm": "60 × 20",
        "water_requirement_mm": "500-700",
        "key_diseases": ["Common Rust", "Gray Leaf Spot"],
    },
    "Apple": {
        "optimal_planting_months": [12, 1, 2],
        "years_to_bearing": 4,
        "season": "Perennial (winter dormancy)",
        "growth_stages": [
            {"stage": "Dormancy", "duration_days": 90, "description": "Winter rest period; prune for shape and airflow."},
            {"stage": "Bud Break", "duration_days": 14, "description": "Buds swell and open; apply pre-bloom fungicide."},
            {"stage": "Bloom", "duration_days": 10, "description": "Pollination critical; avoid spraying during bee activity."},
            {"stage": "Fruit Set", "duration_days": 21, "description": "Thin fruitlets for quality; apply calcium sprays."},
            {"stage": "Fruit Growth", "duration_days": 90, "description": "Monitor for scab and codling moth."},
            {"stage": "Harvest", "duration_days": 30, "description": "Pick at optimal starch index and color."},
        ],
        "spacing_cm": "400 × 400",
        "water_requirement_mm": "700-800",
        "key_diseases": ["Apple Scab", "Black Rot"],
    },
    "Grape": {
        "optimal_planting_months": [1, 2, 3],
        "years_to_bearing": 3,
        "season": "Perennial",
        "growth_stages": [
            {"stage": "Dormancy", "duration_days": 60, "description": "Foundation pruning during winter rest."},
            {"stage": "Bud Break", "duration_days": 14, "description": "New shoots emerge; apply dormant oil spray."},
            {"stage": "Shoot Growth", "duration_days": 30, "description": "Rapid canopy expansion; manage vigor."},
            {"stage": "Flowering", "duration_days": 10, "description": "Avoid overhead irrigation; promote fruit set."},
            {"stage": "Berry Development", "duration_days": 45, "description": "Berry sizing; monitor for downy mildew."},
            {"stage": "Véraison", "duration_days": 14, "description": "Color change; reduce irrigation for quality."},
            {"stage": "Harvest", "duration_days": 14, "description": "Monitor sugar (Brix) and acidity levels."},
        ],
        "spacing_cm": "300 × 150",
        "water_requirement_mm": "500-600",
        "key_diseases": ["Black Rot", "Downy Mildew", "Powdery Mildew"],
    },
    "Bell pepper": {
        "optimal_sowing_months": [7, 8, 9, 10, 1, 2],
        "nursery_days": 30,
        "transplant_to_harvest_days": 70,
        "season": "Kharif / Rabi",
        "growth_stages": [
            {"stage": "Nursery", "duration_days": 30, "description": "Raise seedlings in protected nursery."},
            {"stage": "Transplanting", "duration_days": 7, "description": "Transplant at 4-6 true leaves."},
            {"stage": "Vegetative", "duration_days": 25, "description": "Establish plant structure; stake if needed."},
            {"stage": "Flowering", "duration_days": 15, "description": "Maintain consistent watering; avoid blossom drop."},
            {"stage": "Fruiting", "duration_days": 25, "description": "Monitor for bacterial spot; maintain potassium."},
            {"stage": "Harvest", "duration_days": 21, "description": "Pick at green or full color maturity."},
        ],
        "spacing_cm": "45 × 30",
        "water_requirement_mm": "400-500",
        "key_diseases": ["Bacterial Spot", "Anthracnose"],
    },
}


def get_crop_calendar(crop: str) -> dict[str, Any] | None:
    """Get the planting calendar and growth stages for a specific crop.

    Args:
        crop: Crop name (case-insensitive).

    Returns:
        Crop calendar dict or None if crop not found.
    """
    for name, cal in CROP_CALENDAR.items():
        if name.lower() == crop.lower():
            return {"crop": name, **cal}
    return None


def get_planting_recommendation(crop: str, month: int | None = None) -> dict[str, Any]:
    """Get a planting recommendation for a crop in the current/specified month.

    Returns:
        Dict with is_optimal, message, and current season information.
    """
    if month is None:
        month = datetime.now().month

    calendar = get_crop_calendar(crop)
    season = get_current_season(month)

    if calendar is None:
        return {
            "crop": crop,
            "is_optimal": False,
            "message": f"No calendar data available for '{crop}'. Consult local extension services.",
            "season": season,
        }

    sowing_key = "optimal_sowing_months" if "optimal_sowing_months" in calendar else "optimal_planting_months"
    optimal_months = calendar.get(sowing_key, [])
    is_optimal = month in optimal_months

    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
    }

    if is_optimal:
        message = f"✅ Excellent time to plant {crop}! Current month is within the optimal sowing window."
    else:
        optimal_str = ", ".join(month_names.get(m, str(m)) for m in optimal_months)
        message = f"⚠️ Current month is not optimal for {crop} sowing. Best months: {optimal_str}."

    return {
        "crop": crop,
        "is_optimal": is_optimal,
        "optimal_months": optimal_months,
        "message": message,
        "season": season,
        "key_diseases": calendar.get("key_diseases", []),
        "water_requirement_mm": calendar.get("water_requirement_mm", "N/A"),
    }


def get_rotation_suggestion(current_crop: str) -> dict[str, Any]:
    """Suggest a crop rotation partner based on the current crop.

    Returns:
        Dict with suggested_next_crop, rotation_benefit, and season recommendation.
    """
    rotation_map = {
        "Tomato": ("Corn", "Legume-cereal rotation breaks solanaceous disease cycles."),
        "Potato": ("Wheat", "Cereal rotation reduces late blight inoculum in soil."),
        "Corn": ("Soybean", "Legume fixes nitrogen; improves soil structure."),
        "Apple": ("Cover crop (clover)", "Living mulch improves organic matter and suppresses weeds."),
        "Grape": ("Cover crop (grass)", "Inter-row grass prevents erosion and manages vigor."),
        "Bell pepper": ("Corn", "Non-solanaceous crop breaks bacterial spot cycle."),
    }

    suggestion = rotation_map.get(current_crop)
    if suggestion:
        next_crop, benefit = suggestion
        return {
            "current_crop": current_crop,
            "suggested_next_crop": next_crop,
            "rotation_benefit": benefit,
        }

    return {
        "current_crop": current_crop,
        "suggested_next_crop": "Legume (general)",
        "rotation_benefit": "Legume rotation improves soil nitrogen and breaks pest cycles.",
    }
