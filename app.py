from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from dotenv import load_dotenv, find_dotenv
from gtts import gTTS
import google.generativeai as genai

import qdrant_manager

# --- App bootstrap & Language Configuration -------------------------------- #

PROJECT_ROOT = Path(__file__).resolve().parent

# --- Language and Text Configuration --------------------------------------- #

TRANSLATIONS = {
    "bn": {
        "page_title": "বর্ণবন্ধু – সহজ যোগাযোগের মাধ্যম",
        "app_title": "বর্ণবন্ধু",
        "app_subtitle": "বলুন · বাছুন · শুনুন",
        "speak_button": "🎙️\n\nআমি বলতে চাই",
        "speak_hint": "শুরু করতে একবার চাপ দিন।",
        "intro_card_title": "আমি কথা বলতে চাই",
        "intro_card_body": "বড় বাটনে চাপ দিয়ে শিশু কথা বলা শুরু করতে পারে।",
        "category_card_title": "তুমি কি বলতে চাও?",
        "category_card_body": "শিশুদের সুবিধার জন্য এখানে চারটি বিভাগ রাখা হয়েছে।",
        "phrase_card_title": "তুমি কি বলতে চাও?",
        "phrase_card_body": "প্রাসঙ্গিক তথ্যের উপর ভিত্তি করে, বর্ণবন্ধু আপনাকে বাক্য তৈরি করে দেবে।",
        "voice_card_title": "কথা শুনুন",
        "voice_card_body": "সিস্টেমটি শিশুর জন্য এই বাক্যটি জোরে জোরে বলবে।",
        "stage_1_badge": "ধাপ ১ · শুরু",
        "stage_2_badge": "ধাপ ২ · বিষয়",
        "stage_3_badge": "ধাপ ৩ · পরামর্শ",
        "stage_4_badge": "ধাপ ৪ · শুনুন",
        "tap_sentence_title": "একটি বাক্য বাছাই করুন",
        "show_more_options": "✖ এগুলো নয় · আরও দেখুন",
        "back_to_categories": "← বিভাগ পাতায় ফিরে যান",
        "back_to_intro": "← পিছনে যান",
        "play_again": "▶ আবার বলুন",
        "start_over": "🏠 আবার শুরু করুন",
        "loading_phrases": "বাক্য লোড হচ্ছে...",
        "language_toggle": "English",
        "error_gemini_key": "GEMINI_API_KEY পাওয়া যায়নি। অনুগ্রহ করে আপনার .env ফাইলে এটি যোগ করুন।",
        "error_gemini_model": "Gemini মডেল '{model_name}' চালু করা যায়নি: {e}",
        "info_gemini_model": "আপনার .env ফাইলে GEMINI_MODEL হিসেবে 'gemini-pro' অথবা 'gemini-1.5-pro' সেট করুন।",
        "error_gemini_unavailable": "Gemini মডেল পাওয়া যাচ্ছে না।",
        "error_gemini_empty_response": "Gemini থেকে কোনো উত্তর আসেনি। আবার চেষ্টা করুন।",
        "error_parse_json": "Gemini-এর উত্তরটি JSON ফরম্যাটে পাওয়া যায়নি: {e}",
        "info_parse_json": "Gemini-কে অবশ্যই ৩টি বাক্যসহ একটি ভ্যালিড JSON প্রদান করতে হবে।",
        "error_invalid_format": "Gemini থেকে ভুল ফরম্যাটে উত্তর এসেছে: {e}",
        "info_invalid_format": "Gemini-কে অবশ্যই ৩টি বাক্যসহ একটি ভ্যালিড JSON প্রদান করতে হবে।",
        "error_gemini_api": "Gemini API কল করতে সমস্যা হয়েছে: {e}",
        "info_gemini_api": "অনুগ্রহ করে আপনার API কী এবং মডেলের নাম .env ফাইলে ঠিকভাবে দিন।",
        "warning_qdrant_init": "⚠️ Qdrant চালু করা যায়নি: {e}। অ্যাপটি পার্সোনালাইজেশন ছাড়াই চলবে।",
        "warning_audio_gen": "অডিও তৈরি করা যায়নি: {exc}",
    },
    "en": {
        "page_title": "BornoBuddy – Assistive Communication",
        "app_title": "BornoBuddy",
        "app_subtitle": "Tap · Choose · Speak",
        "speak_button": "🎙️\n\nI want to speak",
        "speak_hint": "Tap once to start.",
        "intro_card_title": "I want to speak",
        "intro_card_body": "One big button to start the conversation.",
        "category_card_title": "What is it about?",
        "category_card_body": "Four simple categories to choose from.",
        "phrase_card_title": "What do you want to say?",
        "phrase_card_body": "AI suggests three simple phrases based on context.",
        "voice_card_title": "Voice Output",
        "voice_card_body": "The device speaks the chosen phrase out loud.",
        "stage_1_badge": "Step 1 · Start",
        "stage_2_badge": "Step 2 · Topic",
        "stage_3_badge": "Step 3 · Suggestion",
        "stage_4_badge": "Step 4 · Voice",
        "tap_sentence_title": "Tap a sentence",
        "show_more_options": "✖ None of these · show more",
        "back_to_categories": "← Back to categories",
        "back_to_intro": "← Back",
        "play_again": "▶ Play again",
        "start_over": "🏠 Start Over",
        "loading_phrases": "Loading phrases...",
        "language_toggle": "বাংলা",
        "error_gemini_key": "GEMINI_API_KEY is missing. Set it in your .env file.",
        "error_gemini_model": "Failed to initialize Gemini model '{model_name}': {e}",
        "info_gemini_model": "Try setting GEMINI_MODEL in .env to 'gemini-pro' or 'gemini-1.5-pro'",
        "error_gemini_unavailable": "Gemini model is not available.",
        "error_gemini_empty_response": "Gemini returned an empty response. Please try again.",
        "error_parse_json": "Failed to parse Gemini response as JSON: {e}",
        "info_parse_json": "Gemini must return valid JSON with exactly 3 phrases.",
        "error_invalid_format": "Invalid response format from Gemini: {e}",
        "info_invalid_format": "Gemini must return exactly 3 phrases.",
        "error_gemini_api": "Error calling Gemini API: {e}",
        "info_gemini_api": "Please check your API key and model name in .env file.",
        "warning_qdrant_init": "⚠️ Qdrant initialization failed: {e}. App will work without personalization.",
        "warning_audio_gen": "Unable to generate audio: {exc}",
    },
}

CATEGORY_CONFIGS = {
    "bn": {
        "শরীর ও চাহিদা": "🍎",
        "অনুভূতি ও সংবেদন": "💛",
        "কাজ ও মানুষ": "🎨",
        "সাহায্য ও সুরক্ষা": "🆘",
    },
    "en": {
        "Body & Needs": "🍎",
        "Feelings & Sensory": "💛",
        "Activities & People": "🎨",
        "Help & Safety": "🆘",
    },
}

def init_session_state() -> None:
    defaults = {
        "stage": "intro",
        "selected_category": None,
        "latitude": None,
        "longitude": None,
        "location_name": None,
        "gps_requested": False,
        "options": [],
        "last_phrase": None,
        "audio_file": None,
        "play_triggered": False,
        "language": "bn",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()
LANG = st.session_state.language
TEXT = TRANSLATIONS[LANG]

st.set_page_config(
    page_title=TEXT["page_title"],
    page_icon="🗣️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

load_dotenv(find_dotenv())

# Force light theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;600;700&display=swap');
    .stApp {
        background: #f0f2f5;
    }
    </style>
""", unsafe_allow_html=True)


MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-pro")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is missing. Set it in your .env file.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

@st.cache_resource
def get_gemini_model():
    try:
        return genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        st.error(TEXT["error_gemini_model"].format(model_name=MODEL_NAME, e=e))
        st.info(TEXT["info_gemini_model"])
        st.stop()
        return None

CHILD_ID = "demo_child"

# --- Helper functions ------------------------------------------------------ #

def get_current_datetime() -> Dict[str, str]:
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "time_of_day": "morning" if now.hour < 12 else "afternoon" if now.hour < 17 else "evening",
    }



def inject_custom_css() -> None:
    st.markdown("""
    <style>
    :root {
        --bg: #f0f2f5; --card: #ffffff; --accent: #006a4e; --accent-soft: #e6f2ed;
        --text: #212121; --muted: #757575; --danger: #f42a41; --radius-lg: 24px;
        --radius-md: 16px; --shadow-md: 0 4px 18px rgba(0, 0, 0, 0.05);
    }
    .main .block-container { max-width: 420px; padding: 1rem; background: transparent; }
    #MainMenu, footer, header, .stDeployButton { display: none !important; }
    button { font-family: 'Hind Siliguri', -apple-system, sans-serif !important; user-select: none; -webkit-user-select: none; }
    .card { background: var(--card); border-radius: var(--radius-lg); padding: 18px; box-shadow: var(--shadow-md); margin-bottom: 1rem; }
    .badge { padding: 2px 8px; border-radius: 999px; font-size: 10px; background: var(--accent-soft); color: var(--accent); display: inline-block; margin-bottom: 0.5rem; font-weight: 600; }
    .hint { font-size: 12px; color: var(--muted); text-align: center; margin-top: 0.5rem; }
    .back-btn { width: 100%; padding: 12px; border-radius: 999px; background: #f0f2f5; color: var(--muted); font-size: 13px; font-weight: 600; border: none; box-shadow: none; cursor: pointer; margin-top: 1rem; }
    .back-btn:hover { background: #e9ecef; }
    .echomind-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
    .echomind-title-wrap { display: flex; align-items: center; gap: 0.75rem; }
    .echomind-title { font-weight: 700; font-size: 22px; color: var(--text); }
    .lang-toggle-btn { font-size: 12px; padding: 6px 10px; border-radius: 999px; background: #e9ecef; color: var(--muted); border: none; font-weight: 600; }
    .lang-toggle-btn:hover { background: #dde1e5; }
    </style>
    """, unsafe_allow_html=True)

def render_header() -> None:
    inject_custom_css()
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f'<div class="echomind-title-wrap"><h1 class="echomind-title">{TEXT["app_title"]}</h1></div>', unsafe_allow_html=True)
    with col2:
        if st.button(TEXT["language_toggle"], key="lang_toggle"):
            st.session_state.language = "en" if LANG == "bn" else "bn"
            st.rerun()


def build_context(category: str) -> Dict[str, str]:
    datetime_info = get_current_datetime()
    location_str = ""
    if st.session_state.latitude and st.session_state.longitude:
        location_str = f"GPS coordinates: {st.session_state.latitude:.6f}, {st.session_state.longitude:.6f}"
        if st.session_state.location_name:
            location_str += f" ({st.session_state.location_name})"
    
    return {
        "child_id": CHILD_ID,
        "category": category,
        "date": datetime_info["date"],
        "time": datetime_info["time"],
        "day_of_week": datetime_info["day_of_week"],
        "time_of_day": datetime_info["time_of_day"],
        "location": location_str if location_str else "Location not available",
        "latitude": str(st.session_state.latitude) if st.session_state.latitude else None,
        "longitude": str(st.session_state.longitude) if st.session_state.longitude else None,
        "last_phrase": st.session_state.get("last_phrase"),
    }


def load_prompt_template(language: str) -> str:
    prompt_file = PROJECT_ROOT / "prompts" / f"suggestion_prompt_{language}.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8").strip()
    # Fallback prompt if file is missing
    return "Generate three short, simple phrases for a non-verbal child."


def parse_model_output(raw_text: str) -> List[Dict[str, str]]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.split("\n", 1)[-1]
    
    data = json.loads(cleaned)

    # Handle two possible formats:
    # Format 1: {"phrases": [...]} - dict with phrases key
    # Format 2: [...] - direct list
    if isinstance(data, dict):
        phrases = data.get("phrases", [])
    elif isinstance(data, list):
        phrases = data
    else:
        raise ValueError(f"Expected dict or list, got {type(data).__name__}")

    if not isinstance(phrases, list):
        raise ValueError("Expected 'phrases' to be a list")
    
    if len(phrases) != 3:
        raise ValueError(f"Expected exactly 3 phrases, got {len(phrases)}")
    
    result = []
    for item in phrases:
        # Handle both formats: dict with "text"/"emoji" or list [text, emoji]
        if isinstance(item, dict):
            text = item.get("text", "").strip()
            emoji = item.get("emoji", "").strip()
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            text = str(item[0]).strip()
            emoji = str(item[1]).strip()
        else:
            raise ValueError(f"Expected dict or [text, emoji] list, got {type(item).__name__}")
        
        if not text:
            raise ValueError("Phrase 'text' field is required and cannot be empty")
        if not emoji:
            raise ValueError("Phrase 'emoji' field is required and cannot be empty")
        
        result.append({"text": text, "emoji": emoji})
    
    return result


def generate_ai_options(category: str, context: Dict[str, str], language: str) -> List[Dict[str, str]]:
    model = get_gemini_model()
    if not model:
        st.error(TEXT["error_gemini_unavailable"])
        st.stop()

    prompt_template = load_prompt_template(language)
    context_lines = [f"{k.replace('_', ' ').title()}: {v}" for k, v in context.items() if v]

    try:
        if st.session_state.get("qdrant_initialized"):
            personalization = qdrant_manager.get_personalization_context(
                child_id=context["child_id"], category=category, context=context)
            if personalization:
                context_lines.append(f"Personalization: {personalization}")
    except Exception as e:
        print(f"Warning: Could not get personalization context: {e}")

    prompt = prompt_template.format(context="\n".join(context_lines))

    try:
        response = model.generate_content(prompt)
        if not getattr(response, "text", "").strip():
            st.error(TEXT["error_gemini_empty_response"])
            st.stop()
        return parse_model_output(response.text)
    except json.JSONDecodeError as e:
        st.error(TEXT["error_parse_json"].format(e=e))
        st.info(TEXT["info_parse_json"])
        st.stop()
    except ValueError as e:
        st.error(TEXT["error_invalid_format"].format(e=e))
        st.info(TEXT["info_invalid_format"])
        st.stop()
    except Exception as e:
        st.error(TEXT["error_gemini_api"].format(e=e))
        st.info(TEXT["info_gemini_api"])
        st.stop()

def fetch_options(category: str, language: str) -> None:
    context = build_context(category)
    phrases = generate_ai_options(category, context, language)
    if not phrases:
        return
    st.session_state.options = [{"id": i, **p} for i, p in enumerate(phrases)]
    st.session_state.stage = "phrases"

def synthesize_audio(text: str, language: str) -> Optional[str]:
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        gTTS(text=text, lang=language).write_to_fp(tmp)
        tmp.close()
        return tmp.name
    except Exception as exc:
        st.warning(TEXT["warning_audio_gen"].format(exc=exc))
        return None


def reset_flow() -> None:
    st.session_state.stage = "intro"
    st.session_state.selected_category = None
    st.session_state.options = []
    st.session_state.last_phrase = None
    st.session_state.audio_file = None
    st.session_state.play_triggered = False


# --- UI Sections ----------------------------------------------------------- #


def inject_custom_css() -> None:
    """Inject custom CSS to match the prototype design - optimized for autistic users"""
    css = """
    <style>
    :root {
        --bg: #f0f2f5;
        --card: #ffffff;
        --accent: #006a4e;
        --accent-soft: #e6f2ed;
        --text: #212121;
        --muted: #757575;
        --danger: #f42a41;
        --radius-lg: 24px;
        --radius-md: 16px;
        --shadow-sm: 0 3px 14px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 18px rgba(0, 0, 0, 0.05);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.06);
    }
    
    /* Force light theme */
    .stApp {
        background: var(--bg) !important;
    }
    
    /* Remove all Streamlit default styling */
    .main .block-container {
        max-width: 420px;
        padding: 1.5rem 1.5rem;
        background: transparent;
    }
    
    /* Hide Streamlit UI elements */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    /* Remove default button styling */
    button {
        font-family: 'Hind Siliguri', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    .echomind-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding: 0.5rem 0;
    }
    
    .echomind-title-wrap {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .bubble-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: var(--accent-soft);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    
    .echomind-title {
        font-weight: 700;
        font-size: 22px;
        margin: 0;
        color: var(--text);
    }
    
    .echomind-subtitle {
        font-size: 12px;
        color: var(--muted);
        margin: 0;
    }
    
    .pill {
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(255,255,255,0.8);
        font-size: 10px;
        color: var(--muted);
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    
    .pill-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent);
    }
    
    .badge {
        padding: 2px 6px;
        border-radius: 999px;
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        background: var(--accent-soft);
        color: var(--muted);
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .primary-btn-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        margin: 2rem 0;
    }
    
    .primary-btn {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        font-size: 18px;
        font-weight: 700;
        background: var(--accent);
        color: white;
        border: none;
        box-shadow: 0 10px 30px rgba(0, 106, 78, 0.4);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        cursor: pointer;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    
    .primary-btn:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 35px rgba(0, 106, 78, 0.5);
    }
    
    .primary-btn:active {
        transform: translateY(0px) scale(0.98);
        box-shadow: 0 6px 20px rgba(0, 106, 78, 0.35);
    }
    
    .primary-btn:focus-visible {
        outline: 3px solid rgba(0, 106, 78, 0.5);
        outline-offset: 4px;
    }
    
    .primary-btn-icon {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background: rgba(255,255,255,0.18);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
    }
    
    .hint {
        font-size: 12px;
        color: var(--muted);
        text-align: center;
        margin-top: 0.5rem;
    }
    
    .card {
        background: var(--card);
        border-radius: var(--radius-lg);
        padding: 18px;
        box-shadow: var(--shadow-md);
        margin-bottom: 1rem;
    }
    
    .tile-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin: 1rem 0;
    }
    
    .tile-btn {
        padding: 18px 14px;
        border-radius: var(--radius-md);
        background: var(--card);
        box-shadow: var(--shadow-md);
        border: 2px solid transparent;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
        cursor: pointer;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        touch-action: manipulation;
        min-height: 140px;
        -webkit-tap-highlight-color: transparent;
    }
    
    .tile-btn:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        border-color: var(--accent-soft);
    }
    
    .tile-btn:active {
        transform: translateY(0px) scale(0.98);
        box-shadow: var(--shadow-sm);
    }
    
    .tile-btn:focus-visible {
        outline: 3px solid var(--accent-soft);
        outline-offset: 2px;
    }
    
    .tile-icon-wrap {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        margin-bottom: 4px;
        text-align: center;
        padding: 4px;
        flex-shrink: 0;
    }
    
    .tile-body .tile-icon-wrap {
        background: #fff3c4;
    }
    
    .tile-feelings .tile-icon-wrap {
        background: #d9eaff;
    }
    
    .tile-activities .tile-icon-wrap {
        background: #ffd6e8;
    }
    
    .tile-safety .tile-icon-wrap {
        background: #ffdede;
    }
    
    .tile-label {
        font-size: 13px;
        font-weight: 600;
        text-align: center;
        color: var(--text);
    }
    
    .tile-sub {
        font-size: 10px;
        color: var(--muted);
        text-align: center;
    }
    
    .suggestion-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin: 1rem 0;
    }
    
    .suggestion-btn {
        width: 100%;
        text-align: left;
        padding: 16px 18px;
        border-radius: var(--radius-md);
        background: var(--card);
        border: 2px solid transparent;
        box-shadow: var(--shadow-sm);
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        touch-action: manipulation;
        min-height: 60px;
        -webkit-tap-highlight-color: transparent;
    }
    
    .suggestion-btn:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        border-color: var(--accent-soft);
    }
    
    .suggestion-btn:active {
        transform: translateY(0px) scale(0.99);
        box-shadow: var(--shadow-sm);
    }
    
    .suggestion-btn:focus-visible {
        outline: 3px solid var(--accent-soft);
        outline-offset: 2px;
    }
    
    .suggestion-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--accent-soft);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        flex-shrink: 0;
    }
    
    .suggestion-text-main {
        font-size: 14px;
        font-weight: 600;
        color: var(--text);
    }
    
    .none-btn {
        width: 100%;
        padding: 14px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        color: var(--danger);
        background: #fee2e2;
        border: 2px solid transparent;
        cursor: pointer;
        margin-top: 0.5rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        touch-action: manipulation;
        min-height: 48px;
    }
    
    .none-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(244, 42, 65, 0.2);
        border-color: rgba(244, 42, 65, 0.3);
    }
    
    .none-btn:active {
        transform: translateY(0px);
    }
    
    .back-btn {
        width: 100%;
        padding: 12px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.9);
        color: var(--muted);
        font-size: 13px;
        font-weight: 600;
        border: 2px solid transparent;
        box-shadow: var(--shadow-sm);
        cursor: pointer;
        margin-top: 1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        touch-action: manipulation;
        min-height: 48px;
    }
    
    .back-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 16px rgba(0, 0, 0, 0.08);
        border-color: var(--accent-soft);
    }
    
    .back-btn:active {
        transform: translateY(0px);
    }
    
    .play-card {
        text-align: center;
        margin: 2rem 0;
    }
    
    .play-icon {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: var(--accent-soft);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 8px;
        font-size: 32px;
    }
    
    .play-phrase {
        font-size: 18px;
        font-weight: 700;
        margin: 1rem 0;
        color: var(--text);
    }
    
    .play-btn {
        margin-top: 10px;
        padding: 12px 20px;
        border-radius: 999px;
        background: var(--accent);
        color: white;
        font-size: 14px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        touch-action: manipulation;
        min-height: 48px;
        box-shadow: 0 4px 12px rgba(0, 106, 78, 0.3);
    }
    
    .play-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 106, 78, 0.4);
    }
    
    .play-btn:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(0, 106, 78, 0.3);
    }
    
    .play-btn:focus-visible {
        outline: 3px solid rgba(0, 106, 78, 0.5);
        outline-offset: 2px;
    }
    
    .section-title {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: var(--text);
    }
    
    /* Accessibility improvements for autistic users */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Improve text readability */
    body, .stApp {
        font-family: 'Hind Siliguri', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        line-height: 1.6 !important;
    }
    
    /* Better contrast for text */
    .card p, .card h2 {
        color: var(--text) !important;
    }
    
    /* Larger touch targets - minimum 44x44px for accessibility */
    button {
        min-height: 44px !important;
        min-width: 44px !important;
    }
    
    /* Smooth animations - not jarring */
    * {
        transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* Remove distracting elements */
    .stApp > div:first-child {
        padding-top: 0 !important;
    }
    
    /* Better spacing for clarity */
    .card {
        margin-bottom: 1.5rem;
    }
    
    /* Ensure emojis are properly sized */
    .tile-icon-wrap, .suggestion-icon, .bubble-icon, .play-icon {
        font-size: inherit !important;
        line-height: 1 !important;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    /* Remove default Streamlit styling and ensure border radius */
    .stButton > button {
        width: 100%;
        border-radius: 16px !important;
    }
    
    /* Default button styling - light colors with border radius */
    button:not([kind="primary"]):not([data-testid*="cat-"]):not([data-testid*="phrase-"]):not([data-testid*="back_"]):not([data-testid*="none_"]):not([data-testid*="play_"]):not([data-testid*="back_home"]) {
        color: #212121 !important;
        background: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 16px !important;
    }
    
    /* Primary buttons keep their accent color */
    button[kind="primary"] {
        color: white !important;
        background: var(--accent) !important;
        border: none !important;
        border-radius: 16px !important;
    }
    
    /* Ensure all buttons have proper border radius as fallback */
    button {
        border-radius: 16px !important;
        user-select: none;
        -webkit-user-select: none;
    }
    
    /* Better focus indicators for keyboard navigation */
    *:focus-visible {
        outline-width: 3px !important;
        outline-style: solid !important;
        outline-offset: 2px !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header() -> None:
    inject_custom_css()
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f'<div class="echomind-title-wrap"><h1 class="echomind-title">{TEXT["app_title"]}</h1></div>', unsafe_allow_html=True)
    with col2:
        if st.button(TEXT["language_toggle"], key="lang_toggle"):
            st.session_state.language = "en" if LANG == "bn" else "bn"
            st.rerun()

    # Progress Indicator
    stage_to_step = {"intro": 1, "categories": 2, "loading": 3, "phrases": 3, "voice": 4}
    current_step = stage_to_step.get(st.session_state.stage, 1)
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <div style="background: #e9ecef; border-radius: 999px; height: 8px;">
            <div style="background: var(--accent); width: {current_step * 25}%; height: 100%; border-radius: 999px; transition: width 0.3s ease-in-out;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stage_intro() -> None:
    st.markdown(f"""
    <div class="card">
        <span class="badge">{TEXT["stage_1_badge"]}</span>
        <h2 style="margin:4px 0;font-size:18px;">{TEXT["intro_card_title"]}</h2>
        <p style="margin:0;font-size:13px;color:var(--muted);">{TEXT["intro_card_body"]}</p>
    </div>
    <style>
    button[data-testid*="speak_main"] {{
        height: 200px !important; border-radius: 50% !important; font-size: 18px !important;
        font-weight: 700 !important; background: var(--accent) !important; color: white !important;
        border: none !important; box-shadow: 0 10px 30px rgba(0, 106, 78, 0.4) !important;
        white-space: pre-line !important; margin: 2rem auto !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if st.button(TEXT["speak_button"], use_container_width=True, type="primary", key="speak_main"):
            st.session_state.stage = "categories"
            st.rerun()
    st.markdown(f'<p class="hint">{TEXT["speak_hint"]}</p>', unsafe_allow_html=True)


def render_categories() -> None:
    st.markdown(f"""
    <div class="card">
        <span class="badge">{TEXT["stage_2_badge"]}</span>
        <h2 style="margin:4px 0;font-size:17px;">{TEXT["category_card_title"]}</h2>
        <p style="margin:0;font-size:12px;color:var(--muted);">{TEXT["category_card_body"]}</p>
    </div>
    <style>
    button[data-testid*="cat-"] {{
        border-radius: 16px !important; background: #ffffff !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.05) !important; border: 2px solid #e2e8f0 !important;
        min-height: 140px !important; font-size: 14px !important; font-weight: 600 !important;
        color: #212121 !important; white-space: pre-line !important; gap: 12px !important;
    }}
    button[data-testid*="cat-"]:hover {{ border-color: var(--accent) !important; }}
    </style>
    """, unsafe_allow_html=True)
    
    categories_list = list(CATEGORY_CONFIGS[LANG].items())
    col1, col2 = st.columns(2)
    
    for i, (label, emoji) in enumerate(categories_list):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            if st.button(f"{emoji}\n\n{label}", key=f"cat-{i}", use_container_width=True):
                st.session_state.selected_category = label
                st.session_state.stage = "loading"
                st.rerun()

    if st.button(f'← {TEXT["back_to_intro"]}', key="back_intro", use_container_width=True):
        reset_flow()
        st.rerun()


def render_phrase_options() -> None:
    st.markdown(f"""
    <div class="card">
        <span class="badge">{TEXT["stage_3_badge"]}</span>
        <h2 style="margin:4px 0;font-size:17px;">{TEXT["phrase_card_title"]}</h2>
        <p style="margin:0;font-size:12px;color:var(--muted);">{TEXT["phrase_card_body"]}</p>
    </div>
    <div style="font-size:14px; font-weight:600; margin-bottom:0.5rem;">{TEXT["tap_sentence_title"]}</div>
    <style>
    button[data-testid*="phrase-"] {{
        text-align: left !important; padding: 18px 20px !important; border-radius: 16px !important;
        background: #ffffff !important; border: 2px solid #e2e8f0 !important;
        box-shadow: 0 3px 14px rgba(0,0,0,0.04) !important; gap: 14px !important;
        margin-bottom: 12px !important; min-height: 64px !important; font-size: 15px !important;
    }}
    button[data-testid*="phrase-"]:hover {{ border-color: var(--accent) !important; }}
    </style>
    """, unsafe_allow_html=True)
    
    for option in st.session_state.options:
        if st.button(f"{option['emoji']}  {option['text']}", key=f"phrase-{option['id']}", use_container_width=True):
            st.session_state.last_phrase = option["text"]
            st.session_state.audio_file = synthesize_audio(option["text"], LANG)
            
            try:
                if st.session_state.get("qdrant_initialized"):
                    qdrant_manager.store_phrase(child_id=CHILD_ID, category=st.session_state.selected_category,
                                                phrase=option["text"], context=build_context(st.session_state.selected_category))
            except Exception as e:
                print(f"Warning: Could not store phrase in Qdrant: {e}")

            st.session_state.stage = "voice"
            st.rerun()
    
    if st.button(TEXT["show_more_options"], key="none_btn", use_container_width=True):
        fetch_options(st.session_state.selected_category, LANG)
        st.rerun()

    if st.button(f'← {TEXT["back_to_categories"]}', key="back_categories", use_container_width=True):
        st.session_state.stage = "categories"
        st.rerun()


def render_voice_output() -> None:
    if not st.session_state.last_phrase:
        st.session_state.stage = "phrases"
        st.rerun()
        return
        
    st.markdown(f"""
    <div class="card">
        <span class="badge">{TEXT["stage_4_badge"]}</span>
        <div style="text-align:center; padding: 1rem 0;">
            <div style="font-size:48px;">🔊</div>
            <h2 style="margin:1rem 0;font-size:20px; font-weight:700;">{st.session_state.last_phrase}</h2>
            <p style="margin:0;font-size:12px;color:var(--muted);">{TEXT["voice_card_body"]}</p>
        </div>
    </div>
    <style>
    button[data-testid*="play_again"] {{
        background: var(--accent) !important; color: white !important; border: none !important;
        border-radius: 999px !important; font-weight: 600 !important; padding: 12px 20px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Give user control over playback
    if st.button(f'▶️ {TEXT["play_again"]}', key="play_again", use_container_width=True):
        if st.session_state.audio_file:
            st.audio(st.session_state.audio_file, autoplay=True)

    if st.button(f'🏠 {TEXT["start_over"]}', key="back_home", use_container_width=True):
        reset_flow()
        st.rerun()

# --- Main Render ----------------------------------------------------------- #

def main() -> None:
    render_header()

    if "qdrant_initialized" not in st.session_state:
        try:
            qdrant_manager.init_qdrant()
            st.session_state.qdrant_initialized = True
        except Exception as e:
            st.warning(TEXT["warning_qdrant_init"].format(e=e))
            st.session_state.qdrant_initialized = False
    
    stage = st.session_state.stage
    if stage == "intro":
        render_stage_intro()
    elif stage == "categories":
        render_categories()
    elif stage == "loading":
        with st.spinner(TEXT["loading_phrases"]):
            fetch_options(st.session_state.selected_category, LANG)
        st.rerun()
    elif stage == "phrases":
        render_phrase_options()
    elif stage == "voice":
        render_voice_output()

if __name__ == "__main__":
    main()
