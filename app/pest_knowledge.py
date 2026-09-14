"""Pest identification knowledge base with remedies for AgriSmart.

Provides structured pest/disease identification data, organic and chemical
treatment options, and severity assessment for common crop pests in India.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Pest & disease knowledge base
# ---------------------------------------------------------------------------

PEST_DATABASE: dict[str, dict[str, Any]] = {
    # ---- TOMATO PESTS & DISEASES ----
    "tomato_whitefly": {
        "common_name": "Whitefly",
        "scientific_name": "Bemisia tabaci",
        "crop": "Tomato",
        "category": "insect",
        "symptoms": [
            "Yellowing and curling of leaves",
            "Sticky honeydew on leaf surfaces",
            "Black sooty mold development",
            "Stunted plant growth",
        ],
        "favorable_conditions": "Hot, dry weather (25-35°C). Thrives in unventilated greenhouses.",
        "organic_remedies": [
            "Yellow sticky traps (25 per acre)",
            "Neem oil spray (3-5 ml/L at weekly intervals)",
            "Release of Encarsia formosa parasitic wasps",
            "Spray with insecticidal soap solution (2%)",
        ],
        "chemical_remedies": [
            "Imidacloprid 17.8% SL (0.3 ml/L) — systemic",
            "Thiamethoxam 25% WG (0.3 g/L) — systemic",
            "Spiromesifen 22.9% SC (1 ml/L) — for nymphs",
        ],
        "prevention": [
            "Use reflective mulch to repel whiteflies",
            "Remove and destroy heavily infested leaves",
            "Maintain weed-free borders around field",
            "Use resistant varieties where available",
        ],
        "severity_levels": {
            "low": "< 5 adults per leaf; yellow traps catching < 10/day",
            "moderate": "5-15 adults per leaf; honeydew visible on lower canopy",
            "severe": "> 15 adults per leaf; sooty mold widespread; yield reduction imminent",
        },
    },
    "tomato_fruit_borer": {
        "common_name": "Tomato Fruit Borer",
        "scientific_name": "Helicoverpa armigera",
        "crop": "Tomato",
        "category": "insect",
        "symptoms": [
            "Circular bore holes in developing fruits",
            "Frass (insect excrement) near entry holes",
            "Premature fruit drop",
            "Internal fruit damage with larval feeding tunnels",
        ],
        "favorable_conditions": "Warm humid conditions during fruiting stage. Peak activity at dusk.",
        "organic_remedies": [
            "Pheromone traps (5 per acre) for monitoring and mass trapping",
            "Bacillus thuringiensis (Bt) spray at early larval stage",
            "Handpicking and destroying infested fruits",
            "Trichogramma egg parasitoid release (50,000 per acre)",
        ],
        "chemical_remedies": [
            "Emamectin benzoate 5% SG (0.4 g/L)",
            "Chlorantraniliprole 18.5% SC (0.3 ml/L)",
            "Spinosad 45% SC (0.3 ml/L) — low toxicity to beneficials",
        ],
        "prevention": [
            "Deep plowing after harvest to expose pupae",
            "Intercropping with marigold as trap crop",
            "Avoid late-season planting in endemic areas",
            "Install bird perches for natural predation",
        ],
        "severity_levels": {
            "low": "< 2% fruit damage; < 1 larva per plant",
            "moderate": "2-10% fruit damage; larvae visible on inspection",
            "severe": "> 10% fruit damage; multiple larvae per plant; economic threshold crossed",
        },
    },

    # ---- POTATO PESTS & DISEASES ----
    "potato_tuber_moth": {
        "common_name": "Potato Tuber Moth",
        "scientific_name": "Phthorimaea operculella",
        "crop": "Potato",
        "category": "insect",
        "symptoms": [
            "Mining tunnels in leaves (serpentine mines)",
            "Silk webbing on foliage",
            "Surface tunneling and boring in stored tubers",
            "Small entry holes in tubers with dark frass",
        ],
        "favorable_conditions": "Warm dry storage. Field infestation increases when soil cracks expose tubers.",
        "organic_remedies": [
            "Pheromone traps for population monitoring",
            "Granulosis virus (GV) biological control agent",
            "Neem leaf powder in storage (layer between potato stacks)",
            "Lantana camara leaf extract spray",
        ],
        "chemical_remedies": [
            "Quinalphos 25% EC (2 ml/L) for field control",
            "DDVP (Dichlorvos) fumigation for stored tubers",
        ],
        "prevention": [
            "Maintain adequate soil coverage (earthing up) to prevent tuber exposure",
            "Harvest promptly at maturity — avoid leaving tubers in field",
            "Maintain cool, well-ventilated storage (< 10°C if possible)",
            "Remove volunteer potato plants from previous seasons",
        ],
        "severity_levels": {
            "low": "< 5% leaf mining; no tuber damage",
            "moderate": "5-15% leaf mining; occasional tuber damage in storage",
            "severe": "> 15% leaf mining; significant tuber damage; storage losses",
        },
    },

    # ---- CORN PESTS ----
    "corn_fall_armyworm": {
        "common_name": "Fall Armyworm",
        "scientific_name": "Spodoptera frugiperda",
        "crop": "Corn",
        "category": "insect",
        "symptoms": [
            "Ragged holes in leaves with translucent window-pane feeding",
            "Copious wet frass in leaf whorls",
            "Skeletonized leaves in severe cases",
            "Larvae feeding on developing ears and tassels",
        ],
        "favorable_conditions": "Warm temperatures (>20°C). Migratory pest — arrival unpredictable.",
        "organic_remedies": [
            "Apply sand + lime mixture (9:1) into whorls to suffocate larvae",
            "Metarhizium rileyi fungal bio-pesticide",
            "Bt (Bacillus thuringiensis var. kurstaki) spray at early instar",
            "Release Telenomus remus egg parasitoids",
        ],
        "chemical_remedies": [
            "Emamectin benzoate 5% SG (0.4 g/L) — whorl application",
            "Chlorantraniliprole 18.5% SC (0.4 ml/L)",
            "Spinetoram 11.7% SC (0.5 ml/L)",
        ],
        "prevention": [
            "Early sowing to avoid peak moth migration period",
            "Intercrop with pulses to support natural enemy populations",
            "Pheromone trap network (5/acre) for early detection",
            "Push-pull technology with Desmodium and Napier grass",
        ],
        "severity_levels": {
            "low": "< 10% plants with fresh window-pane damage",
            "moderate": "10-25% plants with whorl damage; larvae visible",
            "severe": "> 25% plants with severe defoliation; tassel/ear damage",
        },
    },

    # ---- APPLE PESTS ----
    "apple_codling_moth": {
        "common_name": "Codling Moth",
        "scientific_name": "Cydia pomonella",
        "crop": "Apple",
        "category": "insect",
        "symptoms": [
            "Entry holes in fruit, often at calyx end",
            "Frass ('sawdust') at fruit entry points",
            "Internal tunneling toward seed core",
            "Premature fruit drop",
        ],
        "favorable_conditions": "Spring/summer emergence. Flights peak at 15-20°C evenings.",
        "organic_remedies": [
            "Pheromone-based mating disruption dispensers",
            "Kaolin clay particle film spray",
            "Codling moth granulosis virus (CpGV)",
            "Corrugated cardboard trunk bands to trap pupating larvae",
        ],
        "chemical_remedies": [
            "Chlorantraniliprole 18.5% SC (0.3 ml/L) at petal fall",
            "Tebufenozide 20% EC (1 ml/L) — insect growth regulator",
        ],
        "prevention": [
            "Remove and destroy fallen fruit regularly",
            "Bag developing fruits with paper or mesh bags",
            "Maintain orchard sanitation — prune dead wood",
        ],
        "severity_levels": {
            "low": "< 1% fruit with stings at harvest",
            "moderate": "1-5% fruit damage",
            "severe": "> 5% fruit damage; multiple generations active",
        },
    },

    # ---- GRAPE PESTS ----
    "grape_mealybug": {
        "common_name": "Grape Mealybug",
        "scientific_name": "Maconellicoccus hirsutus",
        "crop": "Grape",
        "category": "insect",
        "symptoms": [
            "White waxy cottony masses on stems and bunches",
            "Honeydew secretion and sooty mold",
            "Berry surface contamination",
            "Leaf curling and distortion at growing tips",
        ],
        "favorable_conditions": "Warm humid weather. Sheltered locations on vines.",
        "organic_remedies": [
            "Release of Cryptolaemus montrouzieri predatory beetle",
            "Neem oil spray (5 ml/L)",
            "Soap and water spray to dislodge colonies",
            "Pruning and destroying infested wood during dormancy",
        ],
        "chemical_remedies": [
            "Buprofezin 25% SC (1.5 ml/L) — chitin synthesis inhibitor",
            "Thiamethoxam 25% WG (0.3 g/L) through drip irrigation",
        ],
        "prevention": [
            "Remove bark flakes where mealybugs overwinter",
            "Avoid excess nitrogen fertilization (promotes succulent growth)",
            "Ant management — ants protect mealybug colonies",
        ],
        "severity_levels": {
            "low": "Scattered colonies on trunk and cordons only",
            "moderate": "Colonies reaching bunch stems; honeydew visible",
            "severe": "Heavy infestation on bunches; sooty mold on berries; unmarketable fruit",
        },
    },

    # ---- BELL PEPPER PESTS ----
    "pepper_thrips": {
        "common_name": "Thrips",
        "scientific_name": "Thrips tabaci / Scirtothrips dorsalis",
        "crop": "Bell pepper",
        "category": "insect",
        "symptoms": [
            "Silver-grey streaks and scarring on leaves",
            "Leaf curling and upward cupping",
            "Flower drop and poor fruit set",
            "Bronze discoloration on fruit surface",
        ],
        "favorable_conditions": "Hot dry weather. Thrips migrate from onion and garlic crops nearby.",
        "organic_remedies": [
            "Blue sticky traps (25/acre) for monitoring",
            "Neem oil or Azadirachtin spray (3 ml/L)",
            "Beauveria bassiana fungal bio-pesticide spray",
            "Spinosad 2.5% SC (1 ml/L) — approved for organic use",
        ],
        "chemical_remedies": [
            "Fipronil 5% SC (2 ml/L)",
            "Spinetoram 11.7% SC (0.5 ml/L)",
            "Acephate 75% SP (1.5 g/L) — systemic action",
        ],
        "prevention": [
            "Avoid planting near allium crops (onion, garlic)",
            "Use reflective silver mulch to repel thrips",
            "Maintain field sanitation — remove crop residues",
            "Spray interval rotation to prevent resistance buildup",
        ],
        "severity_levels": {
            "low": "< 5 thrips per flower; no visible leaf damage",
            "moderate": "5-15 thrips per flower; silvering on lower leaves",
            "severe": "> 15 thrips per flower; widespread silvering; flower drop > 30%",
        },
    },
}


# ---------------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------------

def get_pest_info(pest_key: str) -> dict[str, Any] | None:
    """Get detailed pest information by key.

    Args:
        pest_key: Database key (e.g., 'tomato_whitefly').

    Returns:
        Pest info dict or None if not found.
    """
    return PEST_DATABASE.get(pest_key)


def search_pests_by_crop(crop: str) -> list[dict[str, Any]]:
    """Find all pests/diseases for a specific crop.

    Args:
        crop: Crop name (case-insensitive).

    Returns:
        List of pest info dicts matching the crop.
    """
    results = []
    for key, info in PEST_DATABASE.items():
        if info["crop"].lower() == crop.lower():
            results.append({"key": key, **info})
    return results


def search_pests_by_symptom(symptom_keyword: str) -> list[dict[str, Any]]:
    """Search pests by symptom keyword.

    Args:
        symptom_keyword: Keyword to search in symptoms (case-insensitive).

    Returns:
        List of matching pest info dicts with their keys.
    """
    keyword = symptom_keyword.lower()
    results = []
    for key, info in PEST_DATABASE.items():
        for symptom in info.get("symptoms", []):
            if keyword in symptom.lower():
                results.append({"key": key, "matched_symptom": symptom, **info})
                break
    return results


def get_treatment_summary(pest_key: str, prefer_organic: bool = True) -> dict[str, Any] | None:
    """Get a focused treatment summary for a specific pest.

    Args:
        pest_key: Database key for the pest.
        prefer_organic: If True, list organic remedies first.

    Returns:
        Dict with pest name, primary recommendations, and severity guide.
    """
    info = PEST_DATABASE.get(pest_key)
    if info is None:
        return None

    if prefer_organic:
        primary = info.get("organic_remedies", [])
        secondary = info.get("chemical_remedies", [])
        approach = "Organic-first"
    else:
        primary = info.get("chemical_remedies", [])
        secondary = info.get("organic_remedies", [])
        approach = "Chemical-first"

    return {
        "pest": info["common_name"],
        "crop": info["crop"],
        "approach": approach,
        "primary_treatments": primary,
        "alternative_treatments": secondary,
        "prevention_measures": info.get("prevention", []),
        "severity_guide": info.get("severity_levels", {}),
    }


def get_all_crops() -> list[str]:
    """Get a sorted list of all crops covered in the pest database."""
    crops = set()
    for info in PEST_DATABASE.values():
        crops.add(info["crop"])
    return sorted(crops)


def get_pest_count_by_crop() -> dict[str, int]:
    """Get the number of pest/disease entries per crop."""
    counts: dict[str, int] = {}
    for info in PEST_DATABASE.values():
        crop = info["crop"]
        counts[crop] = counts.get(crop, 0) + 1
    return counts
