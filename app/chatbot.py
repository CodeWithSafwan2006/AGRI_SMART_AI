"""Grounded farmer explanations & strict agricultural domain guardrails."""

from __future__ import annotations

import os
import re
from typing import Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

# Keywords indicating agricultural, meteorological, or crop health relevance
AGRI_KEYWORDS = {
    # Crops and plants
    "crop", "crops", "plant", "plants", "leaf", "leaves", "stem", "root", "roots", "canopy",
    "tomato", "potato", "corn", "maize", "apple", "grape", "pepper", "cotton", "wheat",
    "rice", "onion", "chilli", "chili", "mustard", "soybean", "pulse", "pulses", "legume", "legumes",
    "seed", "seeds", "seedling", "seedlings", "vegetable", "vegetables", "fruit", "fruits",
    "horticulture", "grain", "grains", "flower", "flowering", "foliage", "yield", "variety",
    "orchard", "plantation", "sapling", "saplings", "canopy",
    # Diseases, pests & pathology
    "disease", "diseases", "blight", "scab", "rust", "mold", "mould", "rot", "spot", "spots",
    "bacterial", "fungal", "fungus", "fungi", "virus", "viral", "infection", "pest", "pests",
    "insect", "insects", "caterpillar", "aphid", "aphids", "mite", "mites", "worm", "worms",
    "symptom", "symptoms", "cure", "treatment", "treat", "precaution", "precautions", "remedy",
    "remedies", "pathology", "pathogen", "infestation", "damage", "wilt", "wilting", "chlorosis",
    "yellowing", "necrosis", "mildew", "powdery", "downy", "canker", "cankers", "deficiency",
    # Farming practices & inputs
    "spray", "spraying", "sprayer", "fungicide", "fungicides", "pesticide", "pesticides",
    "herbicide", "herbicides", "insecticide", "insecticides", "fertilizer", "fertilizers",
    "manure", "compost", "npk", "urea", "dap", "potash", "nitrogen", "phosphorus", "potassium",
    "micronutrient", "irrigation", "irrigate", "water", "watering", "drip", "prune", "pruning",
    "harvest", "harvesting", "sow", "sowing", "planting", "plant", "soil", "loamy", "clay",
    "sandy", "silt", "black cotton", "acre", "acreage", "plot", "plots", "field", "fields",
    "farm", "farming", "farmer", "agriculture", "agricultural", "agronomy", "agronomic",
    "organic", "dosage", "dose", "neem", "biofertilizer", "mulch", "mulching", "rotation",
    # Weather & Microclimate
    "weather", "rain", "raining", "rainfall", "precipitation", "temperature", "temp", "humidity",
    "moisture", "wind", "windy", "breeze", "velocity", "forecast", "sun", "sunlight", "frost",
    "heat", "heatwave", "climate", "monsoon", "season", "seasonal", "kharif", "rabi", "zaid",
    "dew", "fog", "cloud", "cloudy", "storm", "microclimate", "atmosphere", "atmospheric",
    # Grower inquiry terms
    "advice", "advise", "advisor", "suggest", "suggestion", "recommend", "recommendation",
    "guide", "guidance", "help", "action", "today", "tomorrow", "now", "safe", "prevent",
    "prevention", "protect", "protection", "manage", "management", "risk", "status", "protocol",
    # Multilingual & Transliterated terms (Hindi, Gujarati, Marathi)
    "kisan", "kheti", "fasal", "paudha", "patti", "keeda", "kida", "bimari", "beemari",
    "dawai", "dawa", "aushadh", "paani", "pani", "mausam", "baarish", "barish", "khedut",
    "paak", "roag", "rog", "havaman", "varsad", "shetkari", "sheti", "khat", "khad", "upay",
    # Hindi & Marathi Devanagari script terms
    "फसल", "पौधा", "पौधे", "पत्ती", "पत्तियां", "पत्ते", "कीड़ा", "कीड़े", "कीटनाशक", "कवकनाशी",
    "दवा", "दवाई", "औषध", "रोग", "बीमारी", "झुलसा", "खाद", "उर्वरक", "सिंचाई", "पानी", "छिड़काव",
    "फवारणी", "मौसम", "हवामान", "बारिश", "पाऊस", "तापमान", "नमी", "आर्द्रता", "हवा", "वारा",
    "मिट्टी", "जमीन", "माती", "टमाटर", "आलू", "मक्का", "कपास", "गेहूं", "धान", "चावल", "फल",
    "फूल", "जड़", "तना", "उपाय", "सलाह", "मार्गदर्शन", "किसान", "खेती", "खेत", "शेतकरी", "शेती", "पीक",
    # Gujarati script terms
    "પાક", "છોડ", "પાન", "પાંદડા", "જીવાત", "કીટક", "કીટનાશક", "રોગ", "દવા", "ખાતર", "સિંચાઈ",
    "પાણી", "છંટકાવ", "હવામાન", "વરસાદ", "તાપમાન", "ભેજ", "પવન", "જમીન", "માટી", "ટમેટા",
    "બટાકા", "મકાઈ", "કપાસ", "ઘઉં", "ફળ", "ફૂલ", "ખેડૂત", "ખેતી", "ઉપાય", "સલાહ", "રક્ષણ",
}

OUT_OF_DOMAIN_MESSAGES = {
    "English": "Notice: AgriSmart specializes exclusively in crop pathology, agronomy, and field microclimate intelligence. Please ask a question related to plant health, disease management, spray timing, soil conditions, or weather risks.",
    "Hindi": "सूचना: एग्रीस्मार्ट विशेष रूप से फसल स्वास्थ्य, कृषि और मौसम संबंधी सलाह के लिए डिज़ाइन किया गया है। कृपया फसलों, पौधों की बीमारियों, कीटनाशक/कवकनाशी छिड़काव, खेत की सावधानियों या मौसम से संबंधित प्रश्न पूछें।",
    "Gujarati": "સૂચના: એગ્રીસ્માર્ટ ફક્ત પાક સ્વાસ્થ્ય, ખેતી અને હવામાન સલાહ માટે રચાયેલ છે. કૃપા કરીને પાક, છોડના રોગો, છંટકાવનો સમય અથવા હવામાન સંબંધિત પ્રશ્ન પૂછો.",
    "Marathi": "सूचना: अ‍ॅग्रीस्मार्ट विशेषतः पीक आरोग्य, कृषी सल्ला आणि हवामान व्यवस्थापनासाठी आहे. कृपया पिके, वनस्पतींचे रोग, फवारणी किंवा हवामानाशी संबंधित प्रश्न विचारा.",
}

TRANSLATIONS = {
    "English": {
        "intro": "Canopy Diagnostic Summary:",
        "confidence": "Confidence Index",
        "precautions": "Recommended Field Protocol",
        "weather": "Microclimate Advisory",
    },
    "Hindi": {
        "intro": "पत्ती विश्लेषण परिणाम:",
        "confidence": "सटीकता",
        "precautions": "सुझाए गए उपाय",
        "weather": "मौसम सलाह",
    },
    "Gujarati": {
        "intro": "પાંદડા વિશ્લેષણ પરિણામ:",
        "confidence": "ચોકસાઈ",
        "precautions": "ભલામણ કરેલ પગલાં",
        "weather": "હવામાન માર્ગદર્શન",
    },
    "Marathi": {
        "intro": "पीक तपासणी सारांश:",
        "confidence": "अचूकता",
        "precautions": "शिफारस केलेल्या उपाययोजना",
        "weather": "हवामान सल्ला",
    },
}


def is_agriculture_domain(question: str) -> bool:
    """Check if the user's question belongs to agriculture, crops, or weather domain."""
    if not question or not question.strip():
        return True

    clean_text = question.lower()
    words = re.findall(r"[\w\u0900-\u097F\u0A80-\u0AFF]+", clean_text)

    # General greetings or short affirmative queries
    if len(words) <= 3 and any(w in {"hi", "hello", "namaste", "help", "guide", "info", "thanks", "ok", "yes", "नमस्ते", "નમસ્તે"} for w in words):
        return True

    # Check for presence of any domain keyword or root substring
    for w in words:
        if w in AGRI_KEYWORDS:
            return True
        if any(kw in w for kw in [
            "crop", "farm", "spray", "leaf", "plant", "soil", "rain", "blight", "pestic",
            "fungi", "diseas", "fert", "weed", "seed", "root", "grow", "tomat", "potat",
            "corn", "maiz", "grape", "appl", "cott", "wheat", "irrig", "humid", "temp", "wind"
        ]):
            return True

    # Substring search for Indic phrases
    for kw in AGRI_KEYWORDS:
        if len(kw) >= 3 and kw in clean_text:
            return True

    return False


def get_out_of_domain_reply(language: str = "English") -> str:
    """Return the polite out-of-domain rejection message."""
    return OUT_OF_DOMAIN_MESSAGES.get(language, OUT_OF_DOMAIN_MESSAGES["English"])


def template_explain(
    disease_display: str,
    confidence: float,
    precautions: str,
    weather_tips: list[str],
    language: str = "English",
) -> str:
    t = TRANSLATIONS.get(language, TRANSLATIONS["English"])
    weather_block = " ".join(weather_tips) if weather_tips else "Atmospheric metrics within normal operational bounds."
    if language == "English":
        return (
            f"{t['intro']} {disease_display} ({t['confidence']}: {confidence:.0%}). "
            f"{t['precautions']}: {precautions} "
            f"{t['weather']}: {weather_block}"
        )
    return (
        f"{t['intro']} {disease_display} ({t['confidence']}: {confidence:.0%}). "
        f"{precautions} {weather_block}"
    )


def generate_agronomy_advice(
    question: str,
    disease_display: str,
    confidence: float,
    precautions: str,
    weather_tips: list[str],
    language: str = "English",
    crop: str = "Tomato",
    village: str = "Pune",
    weather_summary: Optional[dict[str, Any]] = None,
) -> str:
    """Generate dynamic, multi-factor agronomic intelligence answering the grower's question."""
    q_clean = question.strip() if question else ""
    sm = weather_summary or {}

    curr_temp = sm.get("current_temp")
    curr_humidity = sm.get("current_humidity")
    max_rain_prob = sm.get("max_rain_prob_24h", 0.0)
    curr_wind = sm.get("current_wind", 0.0)

    # 1. Check for Google Gemini API integration
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        try:
            weather_ctx = (
                f"Location: {village} | Temp: {curr_temp}°C | Humidity: {curr_humidity}% | "
                f"Rain Probability: {max_rain_prob}% | Wind Speed: {curr_wind} km/h"
            )
            prompt = f"""You are an agricultural expert and plant pathologist at AgriSmart.
Grower Location: {village}
Active Crop: {crop}
Leaf Pathology Diagnosis: {disease_display} (Confidence: {confidence:.0%})
Recommended Protocol: {precautions}
Live Microclimate Telemetry: {weather_ctx}
Weather Guidance: {'; '.join(weather_tips) if weather_tips else 'Normal conditions'}
Grower Question: {q_clean or 'Provide crop management and weather advisory.'}

Instruction: Provide clear, concise, actionable advice for the grower in clean, natural {language}. Correlate the question with the live weather metrics and crop pathology. 2-3 precise sentences without boilerplate."""

            preferred_model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
            model_candidates = [preferred_model, "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-pro-latest"]
            for model_name in model_candidates:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                    resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates") or []
                        if candidates:
                            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                            if text:
                                return text
                except Exception:
                    continue
        except Exception:
            pass

    # 2. Check for OpenAI LLM integration if API key is provided
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            weather_ctx = (
                f"Location: {village} | Temp: {curr_temp}°C | Humidity: {curr_humidity}% | "
                f"Rain Probability: {max_rain_prob}% | Wind Speed: {curr_wind} km/h"
            )
            context = f"""
Grower Location: {village}
Active Crop: {crop}
Leaf Pathology: {disease_display} (Confidence: {confidence:.0%})
Recommended Protocol: {precautions}
Telemetry: {weather_ctx}
Weather Guidance: {'; '.join(weather_tips) if weather_tips else 'Normal conditions'}
Grower Question: {q_clean or 'General agronomy advisory'}
"""
            system_prompt = (
                f"You are an expert agronomist and plant pathologist advisor at AgriSmart. "
                f"Provide actionable, grounded advice to the grower in fluent, natural {language}. "
                f"Address their question directly, correlate with live weather parameters and diagnosed pathology, "
                f"and give 2-4 clear, professional sentences without fluff."
            )
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context},
                ],
                max_tokens=250,
                timeout=20,
            )
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text
        except Exception:
            pass

    # Intelligent offline agronomist engine
    is_healthy = "healthy" in disease_display.lower()
    rain_risk = max_rain_prob >= 50
    wind_risk = curr_wind >= 20
    spore_risk = (curr_humidity and curr_humidity >= 75) or (curr_temp and 18 <= curr_temp <= 32 and not is_healthy)

    # Analyze question intent
    q_lower = q_clean.lower()
    is_spray_q = any(k in q_lower for k in ["spray", "spraying", "fungicide", "pesticide", "chemical", "dawai", "chhidkao"])
    is_rain_q = any(k in q_lower for k in ["rain", "baarish", "weather", "precipitation", "mausam", "varsad"])
    is_disease_q = any(k in q_lower for k in ["cure", "treat", "blight", "spot", "mold", "rot", "rust", "bimari", "fungus"])
    is_fert_q = any(k in q_lower for k in ["fertilizer", "nutrient", "npk", "urea", "soil", "manure", "khad"])

    if language == "Hindi":
        parts = []
        if is_spray_q or rain_risk or wind_risk:
            if rain_risk:
                parts.append(f"🌧️ {village} में 24 घंटों में बारिश की संभावना ({max_rain_prob:.0f}%) अधिक है। पत्तियों से दवा धुलने से बचाने के लिए किसी भी छिड़काव को स्थगित करें।")
            elif wind_risk:
                parts.append(f"💨 हवा की गति ({curr_wind:.1f} किमी/घंटा) अधिक है। हवा के बहाव (स्प्रे ड्रिफ्ट) से बचने के लिए हवा शांत होने तक रुकें।")
            else:
                parts.append(f"✅ वर्तमान मौसम छिड़काव के लिए अनुकूल है। सुबह या शाम के शांत समय में अनुशंसित मात्रा में छिड़काव करें।")
        
        if is_disease_q or not is_healthy:
            parts.append(f"🛡️ रोग नियंत्रण ({disease_display}): {precautions}")
        else:
            parts.append(f"🌿 आपकी {crop} फसल वर्तमान में स्वस्थ स्थिति में है। नियमित निगरानी रखें और संतुलित सिंचाई बनाए रखें।")

        if spore_risk and not is_healthy:
            parts.append(f"⚠️ उच्च आर्द्रता ({curr_humidity}%) में फंगल संक्रमण का खतरा बढ़ जाता है। पौधों के बीच उचित वायु संचार बनाए रखें।")

        if q_clean and not parts:
            parts.append(f"सलाह: {precautions} {village} के मौसम के अनुसार सिंचाई और पोषण का प्रबंधन करें।")

        return " ".join(parts)

    elif language == "Gujarati":
        parts = []
        if is_spray_q or rain_risk or wind_risk:
            if rain_risk:
                parts.append(f"🌧️ {village} સ્ટેશન પર વરસાદની સંભાવના ({max_rain_prob:.0f}%) વધારે છે. દવાનો છંટકાવ મોકૂફ રાખો.")
            elif wind_risk:
                parts.append(f"💨 પવનની ગતિ ({curr_wind:.1f} km/h) વધુ છે. સ્પ્રે ડ્રિફ્ટ ટાળવા માટે પવન ધીમો પડે ત્યાં સુધી રાહ જુઓ.")
            else:
                parts.append(f"✅ છંટકાવ માટે હવામાન અનુકૂળ છે. સવારે અથવા સાંજે છંટકાવ કરવો હિતાવહ છે.")
        
        if is_disease_q or not is_healthy:
            parts.append(f"🛡️ રોગ નિયંત્રણ ({disease_display}): {precautions}")
        else:
            parts.append(f"🌿 આપનો {crop} પાક હાલમાં સ્વસ્થ છે. નિયમિત દેખરેખ ચાલુ રાખો.")

        if spore_risk and not is_healthy:
            parts.append(f"⚠️ હવામાં ભેજનું પ્રમાણ ({curr_humidity}%) ઊંચું હોવાથી ફૂગના ફેલાવા પર નજર રાખો.")

        return " ".join(parts)

    elif language == "Marathi":
        parts = []
        if is_spray_q or rain_risk or wind_risk:
            if rain_risk:
                parts.append(f"🌧️ {village} मध्ये पावसाची शक्यता ({max_rain_prob:.0f}%) जास्त आहे. औषध फवारणी तूर्तास पुढे ढकला.")
            elif wind_risk:
                parts.append(f"💨 वाऱ्याचा वेग ({curr_wind:.1f} km/h) जास्त असल्यामुळे फवारणी करणे टाळा.")
            else:
                parts.append(f"✅ सध्याचे हवामान फवारणीसाठी योग्य आहे. सकाळी किंवा संध्याकाळी फवारणी करा.")
        
        if is_disease_q or not is_healthy:
            parts.append(f"🛡️ रोग नियंत्रण ({disease_display}): {precautions}")
        else:
            parts.append(f"🌿 आपले {crop} पीक निरोगी आहे. योग्य पाणी आणि खत व्यवस्थापन सुरू ठेवा.")

        return " ".join(parts)

    else:
        # Default English
        parts = []
        if q_clean:
            parts.append(f"Agronomic Assessment for {crop} at {village} Station:")
        
        if is_spray_q or rain_risk or wind_risk:
            if rain_risk:
                parts.append(f"Precipitation probability is elevated ({max_rain_prob:.0f}% in 24h). Postpone foliar spray applications to prevent product wash-off and chemical loss.")
            elif wind_risk:
                parts.append(f"Wind velocity ({curr_wind:.1f} km/h) exceeds safe application thresholds. Delay mechanical spraying to avoid drift hazard.")
            else:
                parts.append(f"Atmospheric conditions provide an optimal spraying window with low wash-off risk.")

        if is_disease_q or not is_healthy:
            parts.append(f"Pathology Protocol for {disease_display}: {precautions}")
        else:
            parts.append(f"Canopy status indicates a healthy stand. Maintain scheduled scouting and baseline irrigation.")

        if spore_risk and not is_healthy:
            parts.append(f"Elevated relative humidity ({curr_humidity}%) combined with ambient temperature creates a high-risk microclimate for spore propagation; ensure adequate canopy aeration.")

        if is_fert_q:
            parts.append("Maintain balanced nitrogen-phosphorus-potassium nutrition and avoid excess vegetative nitrogen during active infection periods.")

        return " ".join(parts)


def explain_to_farmer(
    disease_display: str,
    confidence: float,
    precautions: str,
    weather_tips: list[str],
    language: str = "English",
) -> str:
    return generate_agronomy_advice(
        question="",
        disease_display=disease_display,
        confidence=confidence,
        precautions=precautions,
        weather_tips=weather_tips,
        language=language,
    )
