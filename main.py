"""
SakhiCare Backend — FastAPI Application
Women's health symptom understanding and care navigation API.

This is a health INFORMATION tool, NOT a diagnostic system.
"""

import os
import re
import json
import time
import logging
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import httpx

# ── Logging ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sakhicare")

# ── App Setup ──
app = FastAPI(
    title="SakhiCare API",
    description="Women's health symptom understanding and care navigation",
    version="1.0.0",
)

# CORS — allow Vite dev server and Capacitor origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8100",
        "capacitor://localhost",
        "http://localhost",
        "https://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from ai_service import get_ai_runtime_status, ask_gemini_assistant, probe_ollama

# ── Ollama Configuration ──
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_TIMEOUT = 25  # seconds


# ══════════════════════════════════════════════
#  PYDANTIC MODELS
# ══════════════════════════════════════════════

class AnalyzeRequest(BaseModel):
    freetext: str = Field(default="", max_length=2000)
    guided_symptoms: list[str] = Field(default_factory=list)
    duration_info: Optional[str] = None
    language_hint: Optional[str] = "en"

    @field_validator("freetext")
    @classmethod
    def sanitize_freetext(cls, v: str) -> str:
        # Strip control characters, keep unicode for Kannada/Hindi
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', v.strip())


class ExtractedSymptom(BaseModel):
    id: str
    original_text: str
    normalized_label: str
    confidence: float = Field(ge=0.0, le=1.0)
    category: Optional[str] = None


class EducationalContent(BaseModel):
    title: str
    summary: str
    source_name: str
    source_url: str
    relevance: str


class SafetyGuidance(BaseModel):
    level: str  # routine | soon | urgent
    message: str
    source: str


class AnalyzeResponse(BaseModel):
    original_input: str
    detected_language: str
    extracted_symptoms: list[ExtractedSymptom]
    clarification_needed: list[str]
    educational_content: list[EducationalContent]
    safety_guidance: SafetyGuidance
    clinician_summary: str
    used_ai: bool
    used_fallback: bool
    disclaimer: str


# ══════════════════════════════════════════════
#  SYMPTOM KNOWLEDGE BASE (deterministic)
# ══════════════════════════════════════════════

# Keyword → normalized symptom mapping for fallback extraction
SYMPTOM_KEYWORDS: dict[str, dict] = {
    # English keywords
    "irregular period": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "irregular menstrual": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "period irregular": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "periods not regular": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "late period": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "missed period": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "no period": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "period stop": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "heavy period": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "heavy bleeding": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "excessive bleeding": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "painful period": {"id": "painful_periods", "label": "Very painful periods", "category": "menstrual"},
    "period pain": {"id": "painful_periods", "label": "Very painful periods", "category": "menstrual"},
    "menstrual cramp": {"id": "painful_periods", "label": "Very painful periods", "category": "menstrual"},
    "bad cramp": {"id": "painful_periods", "label": "Very painful periods", "category": "menstrual"},
    "acne": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "pimple": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "oily skin": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "breakout": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "facial hair": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "excess hair": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "unwanted hair": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "hirsutism": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "hair loss": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "hair thinning": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "hair fall": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "bald": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "dark patch": {"id": "dark_patches", "label": "Dark patches on skin", "category": "skin_hair"},
    "dark skin": {"id": "dark_patches", "label": "Dark patches on skin", "category": "skin_hair"},
    "skin darken": {"id": "dark_patches", "label": "Dark patches on skin", "category": "skin_hair"},
    "weight gain": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "gaining weight": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "putting on weight": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "weight increase": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "can't lose weight": {"id": "difficulty_losing", "label": "Difficulty losing weight", "category": "weight_energy"},
    "hard to lose": {"id": "difficulty_losing", "label": "Difficulty losing weight", "category": "weight_energy"},
    "difficult to lose weight": {"id": "difficulty_losing", "label": "Difficulty losing weight", "category": "weight_energy"},
    "tired": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "fatigue": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "exhausted": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "low energy": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "always tired": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "mood swing": {"id": "mood_changes", "label": "Mood swings or anxiety", "category": "mood_sleep"},
    "anxiety": {"id": "mood_changes", "label": "Mood swings or anxiety", "category": "mood_sleep"},
    "anxious": {"id": "mood_changes", "label": "Mood swings or anxiety", "category": "mood_sleep"},
    "depressed": {"id": "mood_changes", "label": "Mood swings or anxiety", "category": "mood_sleep"},
    "mood change": {"id": "mood_changes", "label": "Mood swings or anxiety", "category": "mood_sleep"},
    "feeling low": {"id": "mood_changes", "label": "Mood swings or anxiety", "category": "mood_sleep"},
    "can't sleep": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "insomnia": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "sleep problem": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "trouble sleeping": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "fertility": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
    "conceive": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
    "trying to get pregnant": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
    "can't get pregnant": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
    "pelvic pain": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "lower abdomen pain": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "stomach pain": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "headache": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    "head pain": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    "migraine": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    # Hindi & Kannada Romanized / Hinglish / Kanglish
    "pet dard": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "pet me dard": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "periods nahi": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "period nahi aa raha": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "periods nahi aa rahe": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "periods late": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "period late": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "periods irregular": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "period irregular": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "irregular periods": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "zyada bleeding": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "bahut dard": {"id": "painful_periods", "label": "Very painful periods", "category": "menstrual"},
    "wajan badh": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "vajan badh": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "wajan kam nahi": {"id": "difficulty_losing", "label": "Difficulty losing weight", "category": "weight_energy"},
    "thakan": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "thakawat": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "baal jhad": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "baal gir": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "chehre par baal": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "chehre pe baal": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "chahre par baal": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "muhase": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "sir dard": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    "sar dard": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    "neend nahi": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "garbh": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
    "bacha nahi": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
    # Kannada romanized / Kanglish
    "hotte novu": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "tale novu": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    "muttu sari illa": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "muttu sariyagi": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "muttu baralla": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "muttu bartilla": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "muttu baruttilla": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "tookanashte": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "tooka hecchu": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "kudalu uduruttide": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "kudalu uduruvudu": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "mukhadalli kudalu": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "susthu": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "ayasa": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
}

# Kannada script keywords
KANNADA_KEYWORDS: dict[str, dict] = {
    "ಮುಟ್ಟು ಸರಿಯಾಗಿ": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "ಮುಟ್ಟು ಬರುತ್ತಿಲ್ಲ": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "ಮುಟ್ಟು ಬರ್ತಿಲ್ಲ": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "ಮುಟ್ಟು ನಿಂತಿದೆ": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "ಮುಟ್ಟಿನ ಸಮಸ್ಯೆ": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "ಅನಿಯಮಿತ ಮುಟ್ಟು": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "ಅನಿಯಮಿತ": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "ಋತುಸ್ರಾವ": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "ಋತುಚಕ್ರ": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "ರಕ್ತಸ್ರಾವ": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "ಹೆಚ್ಚು ರಕ್ತ": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "ಹೊಟ್ಟೆ ನೋವು": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "ಹೊಟ್ಟೆನೋವು": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "ಮುಟ್ಟಿನ ನೋವು": {"id": "painful_periods", "label": "Very painful periods", "category": "menstrual"},
    "ಮೊಡವೆ": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "ಮುಖದಲ್ಲಿ ಕೂದಲು": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "ಅನಗತ್ಯ ಕೂದಲು": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "ಕೂದಲು ಉದುರು": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "ಕೂದಲು ಉದುರುವುದು": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "ತೂಕ ಹೆಚ್ಚ": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "ತೂಕ ಜಾಸ್ತಿ": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "ತೂಕ ಏರಿಕೆ": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "ತೂಕ ಇಳಿಯುತ್ತಿಲ್ಲ": {"id": "difficulty_losing", "label": "Difficulty losing weight", "category": "weight_energy"},
    "ತೂಕ": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "ಸುಸ್ತು": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "ಆಯಾಸ": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "ತಲೆನೋವು": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    "ತಲೆ ನೋವು": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    "ನಿದ್ದೆ ಬರ್ತಿಲ್ಲ": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "ನಿದ್ದೆ": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "ಗರ್ಭಧಾರಣೆ": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
    "ಮಗು ಪಡೆಯಲು": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
}

# Hindi script keywords
HINDI_KEYWORDS: dict[str, dict] = {
    "अनियमित पीरियड्स": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "अनियमित माहवारी": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "अनियमित": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "पीरियड नहीं आ रहे": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "पीरियड्स नहीं आ रहे": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "माहवारी रुक गई": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "पीरियड्स बंद": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "पीरियड लेट": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "पीरियड समय पर नहीं": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "पीरियड": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "माहवारी": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "ज्यादा ब्लीडिंग": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "भारी रक्तस्राव": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "ब्लीडिंग": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "रक्तस्राव": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "पेट दर्द": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "पेट के निचले हिस्से में दर्द": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "पेल्विक दर्द": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "दर्द": {"id": "painful_periods", "label": "Very painful periods", "category": "menstrual"},
    "चेहरे पर बाल": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "अनचाहे बाल": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "चेहरे पर रोएं": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "मुँहासे": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "मुंहासे": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "पिंपल": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "तैलीय त्वचा": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "बाल झड़ रहे": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "बाल गिरना": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "बाल झड़": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "वज़न बढ़ना": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "वजन बढ़ रहा": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "वजन बढ़ गया": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "वज़न घट नहीं रहा": {"id": "difficulty_losing", "label": "Difficulty losing weight", "category": "weight_energy"},
    "वज़न": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "वजन": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "थकान": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "थकावट": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "कमजोरी": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "सुस्ती": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "सिरदर्द": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    "सिर दर्द": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
    "नींद नहीं आती": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "अनिद्रा": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "नींद": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "गर्भधारण में कठिनाई": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
    "गर्भवती नहीं हो पा रही": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
}

CANONICAL_SYMPTOMS: dict[str, dict] = {
    "irregular_periods": {"id": "irregular_periods", "label": "Irregular periods", "category": "menstrual"},
    "missed_periods": {"id": "missed_periods", "label": "Missed periods", "category": "menstrual"},
    "heavy_periods": {"id": "heavy_periods", "label": "Heavy bleeding during periods", "category": "menstrual"},
    "painful_periods": {"id": "painful_periods", "label": "Very painful periods", "category": "menstrual"},
    "acne": {"id": "acne", "label": "Acne or oily skin", "category": "skin_hair"},
    "excess_hair": {"id": "excess_hair", "label": "Excess facial or body hair", "category": "skin_hair"},
    "hair_thinning": {"id": "hair_thinning", "label": "Hair thinning or loss", "category": "skin_hair"},
    "dark_patches": {"id": "dark_patches", "label": "Dark patches on skin", "category": "skin_hair"},
    "weight_gain": {"id": "weight_gain", "label": "Unexplained weight gain", "category": "weight_energy"},
    "difficulty_losing": {"id": "difficulty_losing", "label": "Difficulty losing weight", "category": "weight_energy"},
    "fatigue": {"id": "fatigue", "label": "Persistent tiredness", "category": "weight_energy"},
    "mood_changes": {"id": "mood_changes", "label": "Mood swings or anxiety", "category": "mood_sleep"},
    "sleep_issues": {"id": "sleep_issues", "label": "Trouble sleeping", "category": "mood_sleep"},
    "fertility_concern": {"id": "fertility_concern", "label": "Difficulty conceiving", "category": "other"},
    "pelvic_pain": {"id": "pelvic_pain", "label": "Pelvic pain", "category": "other"},
    "headaches": {"id": "headaches", "label": "Frequent headaches", "category": "other"},
}

def canonicalize_symptom(sym_id: str, label: str, category: str = None) -> tuple[str, str, str]:
    """Map raw AI extracted label or ID to standard clinical label and ID."""
    norm = (label or sym_id or "").lower().strip()
    if norm in CANONICAL_SYMPTOMS:
        c = CANONICAL_SYMPTOMS[norm]
        return c["id"], c["label"], c["category"]

    if any(w in norm for w in ["irregular period", "missed period", "delay", "late period", "cycle irregularity"]):
        c = CANONICAL_SYMPTOMS["irregular_periods"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["facial hair", "excess hair", "body hair", "hirsutism", "unwanted hair"]):
        c = CANONICAL_SYMPTOMS["excess_hair"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["hair fall", "hair loss", "hair thin", "bald"]):
        c = CANONICAL_SYMPTOMS["hair_thinning"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["acne", "pimple", "breakout", "oily skin", "cystic"]):
        c = CANONICAL_SYMPTOMS["acne"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["weight gain", "gaining weight", "putting on weight", "weight"]):
        c = CANONICAL_SYMPTOMS["weight_gain"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["fatigue", "tired", "exhaust", "letharg", "energy", "weakness", "thakan"]):
        c = CANONICAL_SYMPTOMS["fatigue"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["conceiv", "pregnant", "pregnancy", "fertility", "infertility", "baby"]):
        c = CANONICAL_SYMPTOMS["fertility_concern"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["sleep", "insomnia", "sleepless", "can't sleep"]):
        c = CANONICAL_SYMPTOMS["sleep_issues"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["pelvic pain", "cramp", "lower abdomen", "stomach pain", "pelvic"]):
        c = CANONICAL_SYMPTOMS["pelvic_pain"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["heavy bleeding", "heavy period", "flooding bleeding"]):
        c = CANONICAL_SYMPTOMS["heavy_periods"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["painful period", "severe cramp", "dysmenorrhea", "bad cramp"]):
        c = CANONICAL_SYMPTOMS["painful_periods"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["dark patch", "dark skin", "acanthosis"]):
        c = CANONICAL_SYMPTOMS["dark_patches"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["mood", "anxiety", "anxious", "depress"]):
        c = CANONICAL_SYMPTOMS["mood_changes"]
        return c["id"], c["label"], c["category"]
    if any(w in norm for w in ["headache", "migraine"]):
        c = CANONICAL_SYMPTOMS["headaches"]
        return c["id"], c["label"], c["category"]

    clean_id = norm.replace(" ", "_")
    return clean_id, label or norm.title(), category or "other"


# ══════════════════════════════════════════════
#  EDUCATIONAL CONTENT DATABASE
# ══════════════════════════════════════════════

EDUCATIONAL_CONTENT_DB: dict[str, EducationalContent] = {
    "menstrual_general": EducationalContent(
        title="Understanding Menstrual Irregularities",
        summary="Menstrual cycles normally range from 21 to 35 days. Variations can be caused by many factors including stress, weight changes, hormonal conditions such as PCOS, thyroid disorders, and others. A healthcare provider can help determine the cause through examination and tests.",
        source_name="NHS",
        source_url="https://www.nhs.uk/conditions/irregular-periods/",
        relevance="Related to reported menstrual symptoms",
    ),
    "skin_hair": EducationalContent(
        title="Skin & Hair Changes in Women's Health",
        summary="Excess hair growth (hirsutism), acne, and hair thinning can be associated with hormonal imbalances. These symptoms are commonly discussed in the context of conditions like PCOS but can also have other causes. A healthcare provider can evaluate and recommend appropriate tests.",
        source_name="NHS",
        source_url="https://www.nhs.uk/conditions/hirsutism/",
        relevance="Related to reported skin/hair symptoms",
    ),
    "weight_energy": EducationalContent(
        title="Weight & Energy Concerns",
        summary="Unexplained weight changes and persistent fatigue can be related to metabolic, hormonal, or other health factors. Conditions like PCOS, thyroid disorders, and insulin resistance may contribute. A healthcare provider can investigate these symptoms with blood tests and other evaluations.",
        source_name="NHS",
        source_url="https://www.nhs.uk/conditions/polycystic-ovary-syndrome-pcos/",
        relevance="Related to reported weight/energy symptoms",
    ),
    "pcos_overview": EducationalContent(
        title="About PCOS (Polycystic Ovary Syndrome)",
        summary="PCOS is a common hormonal condition affecting an estimated 1 in 10 women of reproductive age. It can cause irregular periods, excess hair growth, acne, weight gain, and fertility concerns. PCOS is diagnosed by a healthcare provider based on a combination of symptoms, blood tests, and ultrasound — not through any app or online tool. Early management can help reduce long-term health risks.",
        source_name="WHO",
        source_url="https://www.who.int/news-room/fact-sheets/detail/polycystic-ovary-syndrome",
        relevance="Your combination of symptoms may be relevant",
    ),
    "general_health": EducationalContent(
        title="Taking Charge of Your Health",
        summary="Tracking and organizing your symptoms is an important step in understanding your health. Bringing a clear summary of your concerns to a healthcare appointment can help your provider give you better care.",
        source_name="WHO",
        source_url="https://www.who.int/health-topics/women-s-health",
        relevance="General health guidance",
    ),
}


# ══════════════════════════════════════════════
#  LANGUAGE DETECTION (simple heuristic)
# ══════════════════════════════════════════════

def detect_language(text: str) -> str:
    """Simple script-based language detection."""
    kannada_range = re.compile(r'[\u0C80-\u0CFF]')
    hindi_range = re.compile(r'[\u0900-\u097F]')

    kannada_count = len(kannada_range.findall(text))
    hindi_count = len(hindi_range.findall(text))
    total = len(text)

    if total == 0:
        return "en"
    if kannada_count > hindi_count and kannada_count > total * 0.1:
        return "kn"
    if hindi_count > kannada_count and hindi_count > total * 0.1:
        return "hi"
    return "en"


# ══════════════════════════════════════════════
#  DETERMINISTIC SYMPTOM EXTRACTION
# ══════════════════════════════════════════════

def extract_symptoms_deterministic(text: str) -> list[ExtractedSymptom]:
    """Extract symptoms using keyword matching (no AI required)."""
    text_lower = text.lower()
    found: dict[str, ExtractedSymptom] = {}

    # Check English/Romanized keywords
    for keyword, info in SYMPTOM_KEYWORDS.items():
        if keyword in text_lower and info["id"] not in found:
            found[info["id"]] = ExtractedSymptom(
                id=info["id"],
                original_text=keyword,
                normalized_label=info["label"],
                confidence=0.85,
                category=info.get("category"),
            )

    # Check Kannada keywords
    for keyword, info in KANNADA_KEYWORDS.items():
        if keyword in text and info["id"] not in found:
            found[info["id"]] = ExtractedSymptom(
                id=info["id"],
                original_text=keyword,
                normalized_label=info["label"],
                confidence=0.75,
                category=info.get("category"),
            )

    # Check Hindi keywords
    for keyword, info in HINDI_KEYWORDS.items():
        if keyword in text and info["id"] not in found:
            found[info["id"]] = ExtractedSymptom(
                id=info["id"],
                original_text=keyword,
                normalized_label=info["label"],
                confidence=0.75,
                category=info.get("category"),
            )

    return list(found.values())


# ══════════════════════════════════════════════
#  OLLAMA AI EXTRACTION (optional)
# ══════════════════════════════════════════════

async def check_ollama_available() -> bool:
    """Check if Ollama is running and the target model is available."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                # Check if our model (or any variant) is available
                for name in model_names:
                    if "qwen" in name.lower():
                        return True
                return len(models) > 0  # Any model available
            return False
    except Exception:
        return False


async def extract_symptoms_ai(text: str, language_hint: str) -> tuple[list[ExtractedSymptom], list[str]]:
    """
    Use Ollama to extract symptoms from freetext.
    Returns (extracted_symptoms, clarification_needed).
    """
    prompt = f"""You are a health information assistant. Extract symptoms from the following user text.
The user may write in English, Hindi, Kannada, or a mix of languages.

IMPORTANT RULES:
- Only extract symptoms that are EXPLICITLY mentioned
- Do NOT infer or diagnose conditions
- If the text is ambiguous, add it to clarification_needed
- Return valid JSON only

User text: "{text}"

Return JSON in this exact format:
{{
  "symptoms": [
    {{"original_text": "exact words from user", "normalized_label": "standardized symptom name", "confidence": 0.9, "category": "menstrual|skin_hair|weight_energy|mood_sleep|other"}}
  ],
  "clarification_needed": ["any ambiguous parts that need clarification"],
  "detected_language": "en|hi|kn|mixed"
}}

Only extract from these categories: irregular periods, missed periods, heavy bleeding, painful periods, acne, excess hair, hair thinning, dark patches, weight gain, difficulty losing weight, fatigue, mood changes, sleep issues, fertility concerns, pelvic pain, headaches.
If periods are absent, delayed, or not coming properly, use "irregular periods" or "missed periods", NEVER "heavy bleeding".

Return ONLY the JSON, no other text."""

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 500},
                },
            )

            if resp.status_code != 200:
                logger.warning(f"Ollama returned status {resp.status_code}")
                return [], []

            response_text = resp.json().get("response", "")
            logger.info(f"Ollama raw response: {response_text[:200]}")

            # Try to parse JSON from the response
            # Handle cases where model wraps in markdown
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                logger.warning("No JSON found in Ollama response")
                return [], ["Could not parse the AI response. Your guided selections are used."]

            parsed = json.loads(json_match.group())

            symptoms = []
            seen_ids = set()
            for s in parsed.get("symptoms", []):
                try:
                    raw_label = s.get("normalized_label", "Unknown")
                    raw_id = s.get("id", raw_label.lower().replace(" ", "_"))
                    c_id, c_label, c_cat = canonicalize_symptom(raw_id, raw_label, s.get("category"))
                    if c_id not in seen_ids:
                        seen_ids.add(c_id)
                        sym = ExtractedSymptom(
                            id=c_id,
                            original_text=s.get("original_text", ""),
                            normalized_label=c_label,
                            confidence=min(max(float(s.get("confidence", 0.5)), 0.0), 1.0),
                            category=c_cat,
                        )
                        symptoms.append(sym)
                except Exception as e:
                    logger.warning(f"Failed to parse symptom: {e}")

            clarifications = parsed.get("clarification_needed", [])
            return symptoms, clarifications

    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error from Ollama: {e}")
        return [], ["The AI response could not be understood. Your guided selections are used."]
    except httpx.TimeoutException:
        logger.warning("Ollama request timed out")
        return [], ["AI analysis timed out. Your guided selections are used."]
    except Exception as e:
        logger.warning(f"Ollama error: {e}")
        return [], ["AI analysis encountered an error. Your guided selections are used."]


# ══════════════════════════════════════════════
#  CONTENT SELECTION (deterministic)
# ══════════════════════════════════════════════

def select_educational_content(symptom_ids: list[str]) -> list[EducationalContent]:
    """Select relevant educational content based on confirmed symptoms."""
    content = []
    categories_found = set()

    menstrual_ids = {"irregular_periods", "heavy_periods", "missed_periods", "painful_periods"}
    skin_hair_ids = {"acne", "excess_hair", "hair_thinning", "dark_patches"}
    weight_ids = {"weight_gain", "difficulty_losing", "fatigue"}

    symptom_set = set(symptom_ids)

    if symptom_set & menstrual_ids:
        content.append(EDUCATIONAL_CONTENT_DB["menstrual_general"])
        categories_found.add("menstrual")

    if symptom_set & skin_hair_ids:
        content.append(EDUCATIONAL_CONTENT_DB["skin_hair"])
        categories_found.add("skin_hair")

    if symptom_set & weight_ids:
        content.append(EDUCATIONAL_CONTENT_DB["weight_energy"])
        categories_found.add("weight_energy")

    # Show PCOS info only when multiple relevant categories are present
    if len(categories_found) >= 2 or (categories_found & {"menstrual"} and len(symptom_set) >= 3):
        content.append(EDUCATIONAL_CONTENT_DB["pcos_overview"])

    if not content:
        content.append(EDUCATIONAL_CONTENT_DB["general_health"])

    return content


def determine_safety_guidance(symptom_ids: list[str], freetext: str) -> SafetyGuidance:
    """
    Determine care guidance level. Based ONLY on verified safety rules.
    Source: NHS urgent symptoms guidance.
    """
    text_lower = freetext.lower()

    # Urgent: check for keywords that suggest an emergency
    # These are based on NHS emergency guidance
    urgent_keywords = [
        "severe pain", "unbearable pain", "fainting", "collapse",
        "can't stop bleeding", "very heavy bleeding", "sudden severe",
        "chest pain", "difficulty breathing", "suicidal", "self harm",
    ]

    for kw in urgent_keywords:
        if kw in text_lower:
            return SafetyGuidance(
                level="urgent",
                message="Some of the symptoms you described may need prompt medical attention. Please contact a healthcare provider or emergency services if you are experiencing severe symptoms.",
                source="NHS urgent care guidance — www.nhs.uk/conditions/periods-heavy/when-to-get-medical-help/",
            )

    # Soon: difficulty conceiving (clinical guidelines recommend reproductive consultation)
    # or severe combination of heavy bleeding with pelvic pain / dysmenorrhea
    has_bleeding_and_pain = "heavy_periods" in symptom_ids and ("pelvic_pain" in symptom_ids or "painful_periods" in symptom_ids)
    if "fertility_concern" in symptom_ids or has_bleeding_and_pain:
        return SafetyGuidance(
            level="soon",
            message="Based on the combination of symptoms you reported, consider scheduling an appointment with a healthcare provider in the coming 1–2 weeks to discuss these concerns.",
            source="NHS & NICE Clinical Guidelines — www.nhs.uk/conditions/infertility/",
        )

    # Routine
    return SafetyGuidance(
        level="routine",
        message="Based on the information you provided, consider scheduling a routine appointment with a healthcare provider to discuss these concerns. If symptoms worsen or you experience severe pain, heavy bleeding, or other urgent symptoms, seek medical care promptly.",
        source="General health guidance — NHS, WHO",
    )


def build_clinician_summary(
    symptom_labels: list[str],
    duration: str,
    freetext: str,
    used_ai: bool,
) -> str:
    """Build a concise summary for the clinician."""
    parts = []
    parts.append(f"Patient self-reports the following symptoms: {', '.join(symptom_labels)}.")
    if duration:
        parts.append(f"Duration reported as: {duration}.")
    if freetext:
        truncated = freetext[:300]
        parts.append(f'Patient also provided this description: "{truncated}".')
    method = "AI-assisted language understanding and guided selection" if used_ai else "guided selection and keyword matching"
    parts.append(f"Symptoms were organized using {method}.")
    parts.append("This information was collected using the SakhiCare symptom organization tool and has not been clinically verified.")
    return " ".join(parts)


class AssistantChatRequest(BaseModel):
    message: str = Field(..., max_length=1500)
    conversation_history: list[dict] = Field(default_factory=list)
    include_symptoms: bool = Field(default=False)
    user_symptoms: list[str] = Field(default_factory=list)


# ══════════════════════════════════════════════
#  API ENDPOINTS
# ══════════════════════════════════════════════

@app.get("/api/health")
async def health_check():
    """Health check endpoint — reports backend, LAN/USB connectivity, and AI status."""
    ai_status = await get_ai_runtime_status()
    return {
        "status": "healthy",
        "service": "SakhiCare 2.0 API",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "ai_status": ai_status,
        "ai_available": ai_status["local_llm"]["available"] or ai_status["gemini_assistant"]["configured"],
    }


@app.get("/api/ai/status")
async def get_ai_status():
    """Return live runtime status of Ollama RTX 5060 local inference and Gemini 3.8 Flash Assistant."""
    return await get_ai_runtime_status()


@app.post("/api/v1/assistant/chat")
async def chat_assistant(request: AssistantChatRequest):
    """
    SakhiCare AI Assistant powered by Google Gemini 3.8 Flash.
    Strictly educational and non-diagnostic; respects user privacy consent for symptoms.
    """
    logger.info(f"Assistant query received: len={len(request.message)}, include_symptoms={request.include_symptoms}")
    result = await ask_gemini_assistant(
        message=request.message,
        conversation_history=request.conversation_history,
        include_symptoms=request.include_symptoms,
        user_symptoms=request.user_symptoms,
    )
    return result


@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze_symptoms(request: AnalyzeRequest):
    """
    Analyze user-reported symptoms.
    Combines guided selection + freetext analysis.
    Falls back to deterministic extraction if AI is unavailable.
    """
    logger.info(f"Analyze request: freetext_len={len(request.freetext)}, guided={len(request.guided_symptoms)}")

    # Validate input
    if not request.freetext and not request.guided_symptoms:
        raise HTTPException(status_code=400, detail="Please provide symptoms via text or guided selection.")

    if len(request.freetext) > 2000:
        raise HTTPException(status_code=400, detail="Text input too long. Please limit to 2000 characters.")

    # Detect language
    detected_language = detect_language(request.freetext) if request.freetext else (request.language_hint or "en")

    # Extract symptoms
    used_ai = False
    extracted_symptoms: list[ExtractedSymptom] = []
    clarification_needed: list[str] = []

    if request.freetext:
        # First try AI
        ai_available = await check_ollama_available()
        if ai_available:
            try:
                ai_symptoms, ai_clarifications = await extract_symptoms_ai(
                    request.freetext, detected_language
                )
                if ai_symptoms:
                    extracted_symptoms = ai_symptoms
                    clarification_needed = ai_clarifications
                    used_ai = True
                    logger.info(f"AI extraction: {len(ai_symptoms)} symptoms found")

                    # Hybrid Ensemble: augment with high-confidence keyword matches for clinical completeness
                    det_symptoms = extract_symptoms_deterministic(request.freetext)
                    existing_ids = {s.id for s in extracted_symptoms}
                    for ds in det_symptoms:
                        if ds.id not in existing_ids:
                            extracted_symptoms.append(ds)
                            existing_ids.add(ds.id)
                            logger.info(f"Hybrid ensemble added keyword match: {ds.normalized_label}")
                else:
                    # AI returned nothing useful — fallback
                    extracted_symptoms = extract_symptoms_deterministic(request.freetext)
                    clarification_needed = ai_clarifications or []
                    logger.info("AI returned no symptoms, using deterministic fallback")
            except Exception as e:
                logger.warning(f"AI extraction failed: {e}")
                extracted_symptoms = extract_symptoms_deterministic(request.freetext)
        else:
            # AI not available — deterministic extraction
            extracted_symptoms = extract_symptoms_deterministic(request.freetext)
            if request.freetext.strip():
                clarification_needed.append(
                    "AI language processing is not available. Symptoms were matched using keyword detection."
                )

    # Combine all symptom IDs (guided + extracted)
    all_symptom_ids = list(set(
        request.guided_symptoms + [s.id for s in extracted_symptoms]
    ))
    all_labels = list(set(
        request.guided_symptoms + [s.normalized_label for s in extracted_symptoms]
    ))

    # Select educational content
    educational_content = select_educational_content(all_symptom_ids)

    # Determine safety guidance
    safety_guidance = determine_safety_guidance(all_symptom_ids, request.freetext)

    # Build clinician summary
    clinician_summary = build_clinician_summary(
        all_labels,
        request.duration_info or "",
        request.freetext,
        used_ai,
    )

    return AnalyzeResponse(
        original_input=request.freetext,
        detected_language=detected_language,
        extracted_symptoms=extracted_symptoms,
        clarification_needed=clarification_needed,
        educational_content=educational_content,
        safety_guidance=safety_guidance,
        clinician_summary=clinician_summary,
        used_ai=used_ai,
        used_fallback=not used_ai,
        disclaimer="SakhiCare is a health information tool only. It does not diagnose medical conditions. Please consult a qualified healthcare professional.",
    )


# ── Run ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
