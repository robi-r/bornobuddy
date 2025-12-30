from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv, find_dotenv
from gtts import gTTS
import google.genai as genai

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
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_dotenv(find_dotenv())


MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-pro")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is missing. Set it in your .env file.")
    st.stop()

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

@st.cache_resource
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)



CHILD_ID = "demo_child"

# --- Helper functions ------------------------------------------------------ #

def get_current_datetime() -> Dict[str, str]:
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "time_of_day": "morning" if now.hour < 12 else "afternoon" if now.hour < 17 else "evening",
        "now": now, # Add the datetime object itself
    }

def inject_custom_css() -> None:
    """Inject custom CSS for a child-friendly, playful design."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Open+Sans:wght@400;600;700&display=swap');

    :root {
        --primary-accent: #FF6F61; /* Cheerful Red-Orange */
        --secondary-accent: #6B8E23; /* Olive Green */
        --tertiary-accent: #FFD700; /* Gold Yellow */
        --pastel-blue: #ADD8E6; /* Light Blue */
        --pastel-green: #90EE90; /* Light Green */
        --pastel-yellow: #FFFACD; /* Lemon Chiffon */
        --pastel-pink: #FFB6C1; /* Light Pink */
        --bg-color: #F8F8F8; /* Soft Off-White Background */
        --card-bg: #FFFFFF; /* White for cards */
        --text-color: #333333; /* Dark Grey for readability */
        --muted-text: #666666; /* Medium Grey for hints */
        --danger-color: #FF4500; /* Orange Red for warnings */
        --border-color: #E0E0E0; /* Light grey border */
        
        --font-family-primary: 'Fredoka One', cursive;
        --font-family-secondary: 'Open Sans', sans-serif;

        --radius-sm: 8px;
        --radius-md: 16px;
        --radius-lg: 20px; /* Large rounded corners for child-friendly */
        --radius-full: 999px;

        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
        --shadow-md: 0 5px 15px rgba(0, 0, 0, 0.12);
        --shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.18);
    }
    
    /* Global Styles */
    body {
        font-family: var(--font-family-secondary);
        color: var(--text-color);
        background: var(--bg-color);
    }

    /* Playful background elements */
    .stApp {
        background-color: var(--bg-color);
        background-image: url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23E0E0E0" fill-opacity="0.2"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6zm30 30v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E');
    }

    /* Increase font sizes globally */
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-family-primary);
        color: var(--primary-accent);
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    h1 { font-size: 2.8rem; }
    h2 { font-size: 2.2rem; }
    h3 { font-size: 1.8rem; }
    p, label, .stMarkdown, .stText {
        font-family: var(--font-family-secondary);
        font-size: 1.15rem; /* Increased body text size */
        line-height: 1.6;
        color: var(--text-color);
    }
    .stMarkdown h2 { color: var(--text-color); } /* Ensure card titles are readable */
    
    /* Ensure high color contrast for readability */
    /* This is implicitly handled by careful choice of var(--text-color) and background */

    /* Generous spacing between elements */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1000px; /* Wider content for wide layout */
    }
    .stVerticalBlock {
        gap: 1.5rem; /* Increased vertical spacing */
    }
    .card {
        background-color: var(--card-bg);
        border-radius: var(--radius-lg);
        padding: 25px; /* More padding for cards */
        margin-bottom: 1.8rem; /* More space between cards */
        box-shadow: var(--shadow-md);
    }

    /* Hide Streamlit UI elements */
    #MainMenu, footer, header, .stDeployButton { display: none !important; }

    /* Button and Interactive Elements Styling */
    button {
        font-family: var(--font-family-primary);
        font-size: 1.3rem; /* Larger font size for buttons */
        min-height: 60px; /* Minimum height for touch-friendly */
        padding: 20px 25px; /* Increased padding */
        border-radius: var(--radius-lg); /* Large rounded corners */
        border: 2px solid var(--border-color); /* Subtle border */
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        user-select: none;
        -webkit-user-select: none;
        touch-action: manipulation;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        color: var(--text-color);
        background-color: var(--card-bg);
        box-shadow: var(--shadow-sm);
    }

    button:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-color: var(--secondary-accent);
    }

    button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }

    button:focus-visible {
        outline: 4px solid var(--pastel-blue);
        outline-offset: 2px;
    }

    /* Primary button specific styles */
    button.primary-btn, button[data-testid*="primary-button"] {
        background-color: var(--primary-accent) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 8px 20px rgba(255, 111, 97, 0.4) !important;
    }
    button.primary-btn:hover, button[data-testid*="primary-button"]:hover {
        background-color: #FF8F81 !important; /* Slightly lighter on hover */
        box-shadow: 0 12px 25px rgba(255, 111, 97, 0.5) !important;
    }

    /* Specific button overrides for larger icons/text */
    [data-testid="stButton-speak_main"] button { /* Main "I want to speak" button */
        width: 250px;
        height: 250px;
        border-radius: var(--radius-full) !important;
        font-size: 1.8rem;
        flex-direction: column;
        gap: 15px;
        background-color: var(--primary-accent) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 8px 20px rgba(255, 111, 97, 0.4) !important;
    }
    [data-testid="stButton-speak_main"] button:hover {
        background-color: #FF8F81 !important; /* Slightly lighter on hover */
        box-shadow: 0 12px 25px rgba(255, 111, 97, 0.5) !important;
    }

    [data-testid="stButton-back_intro"] button,
    [data-testid="stButton-back_to_categories"] button { /* Back buttons */
        background-color: var(--pastel-yellow) !important;
        color: var(--text-color) !important;
        border: 2px solid var(--border-color) !important;
        box-shadow: var(--shadow-sm) !important;
        min-height: 60px;
        border-radius: var(--radius-full);
        font-size: 1.3rem;
    }
    [data-testid="stButton-back_intro"] button:hover,
    [data-testid="stButton-back_to_categories"] button:hover {
        border-color: var(--secondary-accent) !important;
    }
    
    [data-testid*="stButton-phrase_"] button { /* Phrase suggestion buttons */
        min-height: 80px; /* Taller suggestion buttons */
        border-radius: var(--radius-md);
        background-color: var(--card-bg);
        box-shadow: var(--shadow-sm);
        border: 2px solid var(--border-color);
        justify-content: flex-start; /* Align text to start */
        text-align: left; /* Align text to left */
        font-size: 1.25rem; /* Larger text for suggestions */
        font-family: var(--font-family-secondary);
        font-weight: 600;
        color: var(--text-color);
    }
    [data-testid*="stButton-phrase_"] button:hover {
        border-color: var(--pastel-blue);
    }

    [data-testid="stButton-play_again_btn"] button, /* Play again button */
    [data-testid="stButton-start_over_btn"] button { /* Start over button */
        background-color: var(--primary-accent) !important;
        color: white !important;
        border: none !important;
        min-height: 70px;
        border-radius: var(--radius-full);
        font-size: 1.5rem;
        box-shadow: 0 6px 18px rgba(255, 111, 97, 0.4) !important;
    }
    [data-testid="stButton-play_again_btn"] button:hover,
    [data-testid="stButton-start_over_btn"] button:hover {
        background-color: #FF8F81 !important;
        box-shadow: 0 8px 25px rgba(255, 111, 97, 0.5) !important;
    }

    /* General text adjustments */
    .hint {
        font-size: 1rem;
        color: var(--muted-text);
        text-align: center;
        margin-top: 0.8rem;
    }
    .badge {
        font-size: 0.9rem;
        padding: 5px 12px;
        border-radius: var(--radius-full);
        background: var(--pastel-blue);
        color: #333333;
        font-family: var(--font-family-secondary);
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .section-title {
        font-size: 1.4rem;
        font-family: var(--font-family-primary);
        color: var(--primary-accent);
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    /* Header styling */
    .echomind-header {
        padding: 1.5rem 0;
        margin-bottom: 1.5rem;
    }
    .echomind-title-wrap {
        gap: 1rem;
    }
    .echomind-title {
        font-size: 3rem;
        color: var(--primary-accent);
    }
    .echomind-subtitle {
        font-size: 1.2rem;
        color: var(--muted-text);
    }
    [data-testid="stButton-lang_toggle"] button { /* Language toggle button */
        font-size: 1.1rem;
        padding: 12px 20px;
        border-radius: var(--radius-full);
        background: var(--pastel-yellow);
        color: var(--text-color);
        border: 2px solid var(--border-color);
        font-weight: 600;
    }
    [data-testid="stButton-lang_toggle"] button:hover {
        background: #FFEFD5;
        border-color: var(--secondary-accent);
    }

    /* Streamlit specific overrides */
    .stProgress > div > div > div > div {
        background-color: var(--primary-accent);
    }
    .stProgress > div > div > div {
        background-color: var(--pastel-blue);
    }
    .stAlert {
        border-radius: var(--radius-md);
        font-size: 1.1rem;
    }
    .stSpinner > div {
        color: var(--primary-accent);
        font-size: 1.5rem;
    }

    /* Voice Output Card Styling */
    .card.play-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 200px; /* Make the card more prominent */
        background: linear-gradient(135deg, var(--pastel-blue) 0%, var(--pastel-green) 100%); /* Cheerful gradient */
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        box-shadow: var(--shadow-lg);
        border: none;
        padding: 30px;
    }

    .play-card .play-icon {
        font-size: 5rem; /* Large icon for emphasis */
        margin-bottom: 15px;
        line-height: 1;
    }

    .play-card .play-phrase {
        font-family: var(--font-family-primary);
        font-size: 2.5rem; /* Very large text for readability */
        font-weight: bold;
        color: white; /* Ensure text is white for contrast against gradient */
        text-align: center;
        margin: 0;
    }
    
    
    /* General Streamlit button styling - applies to all unless overridden */
    .stButton > button {
        width: 100%;
        font-family: var(--font-family-primary);
        font-size: 1.3rem;
        min-height: 60px;
        padding: 20px 25px;
        border-radius: var(--radius-lg);
        border: 2px solid var(--border-color);
        background-color: var(--card-bg);
        color: var(--text-color);
        box-shadow: var(--shadow-sm);
        display: flex; /* Enable flexbox for content alignment */
        align-items: center; /* Vertically center content */
        justify-content: center; /* Horizontally center content */
        gap: 10px; /* Space between emoji and text */
        transition: all 0.2s ease-in-out;
        user-select: none;
        -webkit-user-select: none;
        touch-action: manipulation;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-color: var(--secondary-accent);
    }
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    .stButton > button:focus-visible {
        outline: 4px solid var(--pastel-blue);
        outline-offset: 2px;
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
        if st.button(TEXT["language_toggle"], key="lang_toggle", help="Toggle language"):
            st.session_state.language = "en" if LANG == "bn" else "bn"
            st.rerun()

    # Progress Indicator
    stage_to_step = {"intro": 1, "categories": 2, "loading": 3, "phrases": 3, "voice": 4}
    current_step = stage_to_step.get(st.session_state.stage, 1)
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <div style="background: #e9ecef; border-radius: 999px; height: 8px;">
            <div style="background: var(--primary-accent); width: {current_step * 25}%; height: 100%; border-radius: 999px; transition: width 0.3s ease-in-out;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


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
        "time_of_day": "morning" if datetime_info["now"].hour < 12 else "afternoon" if datetime_info["now"].hour < 17 else "evening",
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
    client = get_gemini_client()

    prompt_template = load_prompt_template(language)
    context_lines = [f"{k.replace('_', ' ').title()}: {v}" for k, v in context.items() if v]

    try:
        if st.session_state.get("qdrant_initialized"):
            personalization = qdrant_manager.get_personalization_context(
                child_id=context["child_id"],
                category=category,
                context=context
            )
            if personalization:
                context_lines.append(f"Personalization: {personalization}")
    except Exception:
        pass

    prompt = prompt_template.format(context="\n".join(context_lines))

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response.text:
            raise ValueError("Empty Gemini response")

        return parse_model_output(response.text)

    except json.JSONDecodeError as e:
        st.error(TEXT["error_parse_json"].format(e=e))
        st.stop()

    except ValueError as e:
        st.error(TEXT["error_invalid_format"].format(e=e))
        st.stop()

    except Exception as e:
        st.error(TEXT["error_gemini_api"].format(e=e))
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


def render_stage_intro() -> None:
    st.markdown(f"""
    <div class="card">
        <span class="badge">{TEXT["stage_1_badge"]}</span>
        <h2>{TEXT["intro_card_title"]}</h2>
        <p>{TEXT["intro_card_body"]}</p>
    </div>
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
        <h2>{TEXT["category_card_title"]}</h2>
        <p>{TEXT["category_card_body"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    categories_list = list(CATEGORY_CONFIGS[LANG].items())
    col1, col2 = st.columns(2)
    
    for i, (label, emoji) in enumerate(categories_list):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            if st.button(f"{emoji} {label}", key=f"cat-{i}", use_container_width=True):
                st.session_state.selected_category = label
                st.session_state.stage = "loading"
                st.rerun()


    st.markdown("---") # Add a separator for better visual distinction
    if st.button(f'🏠 {TEXT["back_to_intro"]}', key="back_intro", use_container_width=True):
        reset_flow()
        st.rerun()


def render_phrase_options() -> None:
    st.markdown(f"## {TEXT['tap_sentence_title']}")

    # Use a container for phrase options to maintain visual grouping and spacing
    with st.container(border=False):
        for option in st.session_state.options:
            # The button text includes the emoji and the suggested phrase.
            # Styling for "suggestion-btn" is applied via CSS targeting "stButton-phrase_*" data-testid.
            if st.button(f"{option['emoji']}  {option['text']}", 
                         key=f"phrase_{option['id']}", 
                         use_container_width=True):
                st.session_state.last_phrase = option["text"]
                st.session_state.audio_file = synthesize_audio(option["text"], LANG)

                try:
                    if st.session_state.get("qdrant_initialized"):
                        qdrant_manager.store_phrase(
                            child_id=CHILD_ID,
                            category=st.session_state.selected_category,
                            phrase=option["text"],
                            context=build_context(st.session_state.selected_category),
                        )
                except Exception:
                    pass

                st.session_state.stage = "voice"
                st.rerun()

    st.markdown("---") # Add a separator for better visual distinction
    if st.button(TEXT["show_more_options"], key="show_more_options_btn", use_container_width=True):
        st.session_state.stage = "loading"
        st.rerun()

    if st.button(f'← {TEXT["back_to_categories"]}', key="back_to_categories", use_container_width=True):
        st.session_state.stage = "categories"
        st.rerun()



def render_voice_output() -> None:
    if not st.session_state.last_phrase:
        st.session_state.stage = "phrases"
        st.rerun()
        return

    # Use a card for the voice output to make it visually prominent
    st.markdown(f"""
    <div class="card play-card">
        <div style="text-align: center;">
            <span class="play-icon">🔊</span>
            <p class="play-phrase">{st.session_state.last_phrase}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.audio_file and not st.session_state.play_triggered:
        st.audio(st.session_state.audio_file, autoplay=True)
        st.session_state.play_triggered = True

    col1, col2 = st.columns(2)

    with col1:
        # "Play Again" button with an emoji and full width.
        # Styling applied via CSS targeting "stButton-play_again_btn".
        if st.button(f'▶ {TEXT["play_again"]}', key="play_again_btn", use_container_width=True):
            if st.session_state.audio_file: # Only play if audio file exists
                st.audio(st.session_state.audio_file, autoplay=True)

    with col2:
        # "Start Over" button with an emoji and full width.
        # Styling applied via CSS targeting "stButton-start_over_btn".
        if st.button(f'🏠 {TEXT["start_over"]}', key="start_over_btn", use_container_width=True):
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