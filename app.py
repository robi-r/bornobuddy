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
import notifier # Import the new notifier module

# --- App bootstrap & Language Configuration -------------------------------- #

PROJECT_ROOT = Path(__file__).resolve().parent

# --- Language and Text Configuration --------------------------------------- #

OFFLINE_PHRASES = {
    "bn": {
        "শরীর ও চাহিদা": [
            {"text": "আমি পানি চাই", "emoji": "💧"},
            {"text": "আমি ক্ষুধার্ত", "emoji": "🍎"},
            {"text": "আমি বাথরুমে যেতে চাই", "emoji": "🚽"},
        ],
    },
    "en": {
        "Body & Needs": [
            {"text": "I want water", "emoji": "💧"},
            {"text": "I am hungry", "emoji": "🍎"},
            {"text": "I need the bathroom", "emoji": "🚽"},
        ],
    },
}

TRANSLATIONS = {
    "bn": {
        "page_title": "বর্ণবন্ধু – সহজ যোগাযোগের মাধ্যম",
        "app_title": "বর্ণবন্ধু",
        "app_subtitle": "বলুন · বাছুন · শুনুন",
        "speak_button": "🎙️\n\nআমি বলতে চাই",
        "speak_hint": "শুরু করতে একবার চাপ দাও।",
        "intro_card_title": "আমি কথা বলতে চাই",
        "intro_card_body": "বড় বাটনে চাপ দিয়ে তুমি কথা বলা শুরু করতে পারে।",
        "category_card_title": "তুমি কি বলতে চাও?",
        "category_card_body": "শিশুদের সুবিধার জন্য এখানে চারটি বিভাগ রাখা হয়েছে।",
        "phrase_card_title": "তুমি কি বলতে চাও?",
        "phrase_card_body": "প্রাসঙ্গিক তথ্যের উপর ভিত্তি করে, বর্ণবন্ধু তোমাকে বাক্য তৈরি করে দেবে।",
        "voice_card_title": "কথা শুন",
        "voice_card_body": "বর্ণবন্ধু তোমার জন্য এই বাক্যটি জোরে জোরে বলবে।",
        "stage_1_badge": "ধাপ ১ · শুরু",
        "stage_2_badge": "ধাপ ২ · বিষয়",
        "stage_3_badge": "ধাপ ৩ · পরামর্শ",
        "stage_4_badge": "ধাপ ৪ · শুনুন",
        "tap_sentence_title": "একটি বাক্য বাছাই কর",
        "show_more_options": "✖ এগুলো নয় · আরও দেখ",
        "back_to_categories": "← বিভাগ পাতায় ফিরে যাও",
        "back_to_intro": "← পিছনে যাও",
        "play_again": "▶ আবার বলব",
        "start_over": "🏠 আবার শুরু করব",
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
        "say_something_title": "কিছু বলতে চাও?", # New for text input
        "type_phrase_label": "এখানে লিখুন:", # New for text input
        "type_phrase_help": "শিশুটি কী বলতে চায়, তা এখানে টাইপ করুন।", # New for text input
        "predict_phrase_button": "AI এর মাধ্যমে বাক্য তৈরি করুন", # New for text input
        "empty_text_input_warning": "অনুগ্রহ করে কিছু লিখুন।", # New for text input
        "or_type_something": "অথবা কিছু টাইপ করুন", # New for categories page
        "home_button": "🏠 হোম", # New for home button
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
        "say_something_title": "Say Something", # New for text input
        "type_phrase_label": "Type your phrase here:", # New for text input
        "type_phrase_help": "Type what the child wants to say.", # New for text input
        "predict_phrase_button": "Predict Phrase with AI", # New for text input
        "empty_text_input_warning": "Please type something.", # New for text input
        "or_type_something": "or Type Something", # New for categories page
        "home_button": "🏠 Home", # New for home button
    },
}

CATEGORY_CONFIGS = {
    "bn": {
        "আমার শরীর ও প্রয়োজন": "🍎",
        "আমার অনুভূতি জানাতে চাই": "💛",
        "কিছু করতে চাই": "🎨",
        "সাহায্য ও সুরক্ষা চাই": "🆘",
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
        "predicted_phrase": None, # New: Stores the AI-predicted phrase from text input
        "text_input_value": "", # New: Stores the value from the text input box
        "emoji_only": False,
        "previous_stage": "intro", # New: Track the previous stage for back navigation
        "predicted_audio_file": None, # New: Store audio file for predicted phrase
        "phrase_predicted": False, # New: Flag to indicate if a phrase has been predicted
        "play_count": 0, # For forcing audio replay
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
#client = genai.Client(api_key=GEMINI_API_KEY)

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

@st.cache_data(hash_funcs={gTTS: lambda _: None})
def synthesize_audio(text: str, language: str) -> Optional[str]:
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        gTTS(text=text, lang=language).write_to_fp(tmp)
        tmp.close()
        return tmp.name
    except Exception as exc:
        st.warning(TEXT["warning_audio_gen"].format(exc=exc))
        return None


def inject_custom_css() -> None:
    """Inject custom CSS for a child-friendly, playful design."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Open+Sans:wght@400;600;700&display=swap');

    :root {
        --primary-accent: #64B5F6; /* Cheerful Light Blue */
        --secondary-accent: #81C784; /* Soft Green */
        --tertiary-accent: #FFD54F; /* Sunny Yellow */
        --pastel-blue: #BBDEFB; /* Lighter Blue */
        --pastel-green: #C8E6C9; /* Lighter Green */
        --pastel-yellow: #FFF9C4; /* Lighter Yellow */
        --pastel-pink: #FFCDD2; /* Lighter Pink */
        --bg-color: #FDFDFD; /* Very Soft Off-White Background */
        --card-bg: #FFFFFF; /* White for cards, still clean */
        --text-color: #424242; /* Darker, softer Grey for readability */
        --muted-text: #9E9E9E; /* Medium Grey for hints */
        --danger-color: #EF9A9A; /* Soft Red for warnings */
        --border-color: #E0E0E0; /* Light grey border */
        
        --font-family-primary: 'Fredoka One', cursive;
        --font-family-secondary: 'Open Sans', sans-serif;

        --radius-sm: 10px;
        --radius-md: 18px;
        --radius-lg: 25px; /* More rounded corners for child-friendly */
        --radius-full: 999px;

        --shadow-sm: 0 3px 10px rgba(0, 0, 0, 0.07);
        --shadow-md: 0 7px 20px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 12px 35px rgba(0, 0, 0, 0.15);
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
        margin-top: 1.2rem; /* Slightly more vertical space */
        margin-bottom: 0.6rem;
    }
    h1 { font-size: 3rem; } /* Slightly larger h1 */
    h2 { font-size: 2.4rem; }
    h3 { font-size: 2rem; }
    p, label, .stMarkdown, .stText {
        font-family: var(--font-family-secondary);
        font-size: 1.2rem; /* Increased body text size */
        line-height: 1.7; /* Slightly more line height for readability */
        color: var(--text-color);
    }
    .stMarkdown h2 { color: var(--text-color); } /* Ensure card titles are readable */
    
    /* Ensure high color contrast for readability */
    /* This is implicitly handled by careful choice of var(--text-color) and background */

    /* Generous spacing between elements */
    .block-container {
        padding-top: 2.5rem; /* More padding */
        padding-bottom: 2.5rem;
        max-width: 1000px; /* Wider content for wide layout */
    }
    .stVerticalBlock {
        gap: 1.8rem; /* Increased vertical spacing */
    }
    .card {
        background-color: var(--card-bg);
        border-radius: var(--radius-lg);
        padding: 30px; /* More padding for cards */
        margin-bottom: 2rem; /* More space between cards */
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color); /* Subtle border for definition */
    }

    /* Hide Streamlit UI elements */
    #MainMenu, footer, header, .stDeployButton { display: none !important; }

    /* Button and Interactive Elements Styling */
    button {
        font-family: var(--font-family-primary);
        font-size: 1.4rem; /* Larger font size for buttons */
        min-height: 65px; /* Minimum height for touch-friendly */
        padding: 22px 28px; /* Increased padding */
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
        gap: 12px;
        color: var(--text-color);
        background-color: var(--card-bg);
        box-shadow: var(--shadow-sm);
    }

    button:hover {
        transform: translateY(-4px); /* More pronounced lift */
        box-shadow: var(--shadow-md);
        border-color: var(--secondary-accent);
    }

    button:active {
        transform: translateY(-1px); /* Slightly sink */
        box-shadow: var(--shadow-sm);
    }

    button:focus-visible {
        outline: 4px solid var(--pastel-blue);
        outline-offset: 3px; /* More prominent focus indicator */
    }

    /* Primary button specific styles */
    button.primary-btn, button[data-testid*="primary-button"] {
        background-color: var(--primary-accent) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(100, 181, 246, 0.4) !important; /* Adjusted shadow to match new primary color */
    }
    button.primary-btn:hover, button[data-testid*="primary-button"]:hover {
        background-color: #79BFFD !important; /* Slightly lighter on hover */
        box-shadow: 0 14px 30px rgba(100, 181, 246, 0.5) !important;
    }

    /* Specific button overrides for larger icons/text */
    [data-testid="stButton-speak_main"] button { /* Main "I want to speak" button */
        width: 260px; /* Slightly larger */
        height: 260px;
        border-radius: var(--radius-full) !important;
        font-size: 2rem; /* Larger font */
        flex-direction: column;
        gap: 18px;
        background-color: var(--primary-accent) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(100, 181, 246, 0.4) !important;
    }
    [data-testid="stButton-speak_main"] button:hover {
        background-color: #79BFFD !important; /* Slightly lighter on hover */
        box-shadow: 0 14px 30px rgba(100, 181, 246, 0.5) !important;
    }

    [data-testid="stButton-back_intro"] button,
    [data-testid="stButton-back_to_categories"] button { /* Back buttons */
        background-color: var(--pastel-yellow) !important;
        color: var(--text-color) !important;
        border: 2px solid var(--border-color) !important;
        box-shadow: var(--shadow-sm) !important;
        min-height: 65px;
        border-radius: var(--radius-full);
        font-size: 1.4rem;
    }
    [data-testid="stButton-back_intro"] button:hover,
    [data-testid="stButton-back_to_categories"] button:hover {
        border-color: var(--secondary-accent) !important;
        background-color: #FFECB3 !important; /* Slightly lighter yellow on hover */
    }
    
    [data-testid*="stButton-phrase_"] button { /* Phrase suggestion buttons */
        min-height: 85px; /* Taller suggestion buttons */
        border-radius: var(--radius-md);
        background-color: var(--card-bg);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color); /* Thinner border */
        justify-content: flex-start; /* Align text to start */
        text-align: left; /* Align text to left */
        font-size: 1.3rem; /* Larger text for suggestions */
        font-family: var(--font-family-secondary);
        font-weight: 600;
        color: var(--text-color);
    }
    [data-testid*="stButton-phrase_"] button:hover {
        border-color: var(--primary-accent); /* Blue border on hover */
        background-color: var(--pastel-blue); /* Light blue background on hover */
    }

    [data-testid="stButton-play_again_btn"] button, /* Play again button */
    [data-testid="stButton-start_over_btn"] button { /* Start over button */
        background-color: var(--primary-accent) !important;
        color: white !important;
        border: none !important;
        min-height: 75px;
        border-radius: var(--radius-full);
        font-size: 1.6rem;
        box-shadow: 0 8px 20px rgba(100, 181, 246, 0.4) !important;
    }
    [data-testid="stButton-play_again_btn"] button:hover,
    [data-testid="stButton-start_over_btn"] button:hover {
        background-color: #79BFFD !important;
        box-shadow: 0 10px 25px rgba(100, 181, 246, 0.5) !important;
    }

    /* General text adjustments */
    .hint {
        font-size: 1.05rem;
        color: var(--muted-text);
        text-align: center;
        margin-top: 1rem;
    }
    .badge {
        font-size: 0.95rem;
        padding: 6px 14px;
        border-radius: var(--radius-full);
        background: var(--pastel-blue);
        color: var(--text-color); /* Darker text for badges */
        font-family: var(--font-family-secondary);
        font-weight: 600;
        letter-spacing: 0.06em;
    }
    .section-title {
        font-size: 1.5rem;
        font-family: var(--font-family-primary);
        color: var(--primary-accent);
        margin-top: 1.8rem;
        margin-bottom: 0.9rem;
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
        font-size: 3.2rem;
        color: var(--primary-accent);
    }
    .echomind-subtitle {
        font-size: 1.3rem;
        color: var(--muted-text);
    }
    [data-testid="stButton-lang_toggle"] button { /* Language toggle button */
        font-size: 1.15rem;
        padding: 14px 22px;
        border-radius: var(--radius-full);
        background: var(--pastel-yellow);
        color: var(--text-color);
        border: 2px solid var(--border-color);
        font-weight: 600;
    }
    [data-testid="stButton-lang_toggle"] button:hover {
        background: #FFECB3;
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
        font-size: 1.15rem;
    }
    .stSpinner > div {
        color: var(--primary-accent);
        font-size: 1.6rem;
    }

    /* Ensuring emojis scale correctly */
    .emoji, .stButton > button .emoji {
        font-size: 1.8em; /* Significantly larger emojis */
        line-height: 1;
        vertical-align: middle;
    }

    /* Adjust Streamlit default button to match custom styling */
    .stButton > button {
        width: 100%;
        font-family: var(--font-family-primary);
        font-size: 1.5rem; /* Slightly larger button text */
        min-height: 75px; /* Taller buttons */
        padding: 22px 28px;
        border-radius: var(--radius-lg);
        border: 2px solid var(--border-color);
        background-color: var(--card-bg);
        color: var(--text-color);
        box-shadow: var(--shadow-sm);
        display: flex; /* Enable flexbox for content alignment */
        align-items: center; /* Vertically center content */
        justify-content: center; /* Horizontally center content */
        gap: 15px; /* More space between emoji and text */
        transition: all 0.2s ease-in-out;
        user-select: none;
        -webkit-user-select: none;
        touch-action: manipulation;
    }
    .stButton > button:hover {
        transform: translateY(-5px); /* More pronounced lift on hover */
        box-shadow: var(--shadow-lg); /* Stronger shadow on hover */
        border-color: var(--secondary-accent);
    }
    .stButton > button:active {
        transform: translateY(-2px); /* Slightly sink */
        box-shadow: var(--shadow-md);
    }
    .stButton > button:focus-visible {
        outline: 4px solid var(--pastel-blue);
        outline-offset: 4px; /* More prominent focus indicator */
    }

    /* Override for phrase buttons to ensure emoji is large and text aligns */
    [data-testid*="stButton-phrase_"] button { /* Phrase suggestion buttons */
        min-height: 100px; /* Even taller suggestion buttons */
        border-radius: var(--radius-lg); /* Larger rounded corners */
        background-color: var(--card-bg);
        box-shadow: var(--shadow-md); /* Slightly stronger shadow */
        border: 2px solid var(--border-color); /* More visible border */
        justify-content: flex-start; /* Align text to start */
        text-align: left; /* Align text to left */
        font-size: 1.5rem; /* Larger text for suggestions */
        font-family: var(--font-family-primary); /* Use primary font for phrases */
        font-weight: 700; /* Bolder text */
        color: var(--text-color);
        padding-left: 30px; /* More padding */
        padding-right: 30px;
    }
    [data-testid*="stButton-phrase_"] button:hover {
        border-color: var(--primary-accent); /* Blue border on hover */
        background-color: var(--pastel-blue); /* Light blue background on hover */
    }
    [data-testid*="stButton-phrase_"] button > div > p { /* Target text within phrase buttons */
        font-size: 1.5rem; /* Ensure text scales with button */
        font-family: var(--font-family-primary);
        font-weight: 700;
        margin: 0;
    }
    [data-testid*="stButton-phrase_"] button > div > div:first-child { /* Target emoji container */
        font-size: 6.0rem; /* Even larger emoji for phrase buttons */
        line-height: 1;
        margin-right: 15px;
    }

    /* Specific button overrides for larger icons/text */
    [data-testid="stButton-speak_main"] button { /* Main "I want to speak" button */
        width: 300px; /* Even larger */
        height: 300px;
        border-radius: var(--radius-full) !important;
        font-size: 2.5rem; /* Larger font */
        flex-direction: column;
        gap: 20px;
        background-color: var(--primary-accent) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 12px 30px rgba(100, 181, 246, 0.5) !important; /* Stronger shadow */
    }
    [data-testid="stButton-speak_main"] button:hover {
        background-color: #8CC0FA !important; /* Slightly lighter on hover */
        box-shadow: 0 16px 35px rgba(100, 181, 246, 0.6) !important;
    }
    [data-testid="stButton-speak_main"] button > div > p {
        font-size: 2.5rem;
        margin: 0;
    }
    [data-testid="stButton-speak_main"] button > div > div:first-child {
        font-size: 3.5rem; /* Very large emoji for main button */
    }
    
    [data-testid="stButton-play_again_btn"] button, /* Play again button */
    [data-testid="stButton-start_over_btn"] button { /* Start over button */
        background-color: var(--primary-accent) !important;
        color: white !important;
        border: none !important;
        min-height: 85px; /* Taller */
        border-radius: var(--radius-full);
        font-size: 1.8rem;
        box-shadow: 0 10px 25px rgba(100, 181, 246, 0.4) !important;
    }
    [data-testid="stButton-play_again_btn"] button:hover,
    [data-testid="stButton-start_over_btn"] button:hover {
        background-color: #79BFFD !important;
        box-shadow: 0 12px 30px rgba(100, 181, 246, 0.5) !important;
    }

    .play-card .play-icon { /* Specific style for the voice output emoji */
        font-size: 5rem; /* Very large play icon */
        margin-bottom: 20px;
        line-height: 1;
    }
    .play-card .play-phrase { /* Text in the play card */
        font-size: 2.5rem; /* Very large text for the spoken phrase */
        font-family: var(--font-family-primary);
        color: var(--primary-accent);
        text-align: center;
        margin-bottom: 20px;
    }
    .play-card .hint {
        font-size: 1.2rem;
        text-align: center;
    }

    /* Text input stage buttons */
    [data-testid="stButton-predict_button"] button {
        background-color: var(--secondary-accent) !important;
        color: white !important;
        box-shadow: 0 8px 20px rgba(129, 199, 132, 0.4) !important;
    }
    [data-testid="stButton-predict_button"] button:hover {
        background-color: #90D493 !important;
        box-shadow: 0 10px 25px rgba(129, 199, 132, 0.5) !important;
    }

    /* Category buttons */
    [data-testid*="stButton-cat-"] button {
        min-height: 120px; /* Larger category buttons */
        border-radius: var(--radius-md);
        font-size: 1.8rem; /* Larger font for category labels */
        font-family: var(--font-family-primary);
        font-weight: 700;
        gap: 15px;
    }
    [data-testid*="stButton-cat-"] button > div > div:first-child {
        font-size: 5.5rem; /* Large emoji for category buttons */
    }

    /* General text input styling */
    div[data-testid="stText"] {
        font-size: 1.5rem;
    }
    label[data-testid="stWidgetLabel"] {
        font-size: 1.3rem;
        font-family: var(--font-family-primary);
        color: var(--text-color);
        margin-bottom: 10px;
    }
    textarea[data-testid="stTextArea"], input[data-testid="stTextInput"] {
        font-size: 1.4rem;
        padding: 15px 20px;
        border-radius: var(--radius-md);
        border: 2px solid var(--border-color);
        background-color: var(--card-bg);
        color: var(--text-color);
    }
    textarea[data-testid="stTextArea"]:focus, input[data-testid="stTextInput"]:focus {
        border-color: var(--primary-accent);
        box-shadow: 0 0 0 3px rgba(100, 181, 246, 0.3);
    }
    
    /* Ensure high color contrast for readability */
    /* This is implicitly handled by careful choice of var(--text-color) and background */

    /* Generous spacing between elements */
    .block-container {
        padding-top: 3rem; /* More padding */
        padding-bottom: 3rem;
        max-width: 1100px; /* Even wider content for wide layout */
    }
    .stVerticalBlock {
        gap: 2rem; /* Increased vertical spacing */
    }
    .card {
        padding: 40px; /* More padding for cards */
        margin-bottom: 2.5rem; /* More space between cards */
    }

    /* Overall font size increases */
    h1 { font-size: 3.5rem; } /* Larger h1 */
    h2 { font-size: 2.8rem; } /* Larger h2 */
    h3 { font-size: 2.2rem; } /* Larger h3 */
    p, label, .stMarkdown, .stText {
        font-size: 1.3rem; /* Increased body text size */
    }
    .hint {
        font-size: 1.15rem; /* Larger hint text */
    }
    .badge {
        font-size: 1.05rem; /* Larger badge text */
        padding: 8px 16px;
    }
    .echomind-title {
        font-size: 3.8rem; /* Even larger app title */
    }
    .echomind-subtitle {
        font-size: 1.4rem; /* Larger subtitle */
    }
    [data-testid="stButton-lang_toggle"] button { /* Language toggle button */
        font-size: 1.25rem;
        padding: 16px 24px;
    }
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_header() -> None:

    if st.button("😊 Emoji Only", key="emoji_toggle"):
        st.session_state.emoji_only = not st.session_state.emoji_only
        st.rerun()

    inject_custom_css()
    col_home, col_title, col_lang = st.columns([1, 4, 1])
    with col_home:
        if st.button(TEXT["home_button"], key="home_button_nav", use_container_width=True):
            reset_flow()
            st.rerun()
    with col_title:
        st.markdown(f'<div class="echomind-title-wrap"><h1 class="echomind-title">{TEXT["app_title"]}</h1></div>', unsafe_allow_html=True)
    with col_lang:
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

def load_predict_intent_prompt_template(language: str) -> str:
    prompt_file = PROJECT_ROOT / "prompts" / f"predict_intent_prompt_{language}.txt"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8").strip()
    # Fallback prompt if file is missing
    return "Rephrase the child's input into a simple, single phrase."


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


def predict_intent(child_input: str, language: str) -> Dict[str, str]:
    client = get_gemini_client()
    # Load the prompt template
    prompt_template = load_predict_intent_prompt_template(language)
    
    # Escape JSON braces in the template to avoid KeyError
    prompt_template = prompt_template.replace("{", "{{").replace("}", "}}")
    
    # Now safely replace our variables
    prompt_template = prompt_template.replace("{{child_input}}", "{child_input}")
    prompt_template = prompt_template.replace("{{context}}", "{context}")
    
    # Build context
    context_data = build_context("Text Input")  # Use a generic category for context
    context_lines = [f"{k.replace('_', ' ').title()}: {v}" for k, v in context_data.items() if v]

    # Fill in the template
    prompt = prompt_template.format(context="\n".join(context_lines), child_input=child_input)

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response.text:
            raise ValueError("Empty Gemini response")
        
        parsed_response = json.loads(
            response.text.strip()
            .replace("```json", "")
            .replace("```", "")
        )
        if not isinstance(parsed_response, dict) or "text" not in parsed_response or "emoji" not in parsed_response:
            raise ValueError("Invalid JSON format from Gemini. Expected {'text': '...', 'emoji': '...'}")

        return parsed_response

    except json.JSONDecodeError as e:
        st.error(f"Failed to parse Gemini response for intent prediction as JSON: {e}")
        st.stop()
    except ValueError as e:
        st.error(f"Invalid response format from Gemini for intent prediction: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error calling Gemini API for intent prediction: {e}")
        st.stop()


def fetch_options(category: str, language: str) -> None:
    context = build_context(category)
    try:
        phrases = generate_ai_options(category, context, language)
    except Exception:
        phrases = OFFLINE_PHRASES.get(language, {}).get(category, [])

    if not phrases:
        return
    st.session_state.options = [{"id": i, **p} for i, p in enumerate(phrases)]
    st.session_state.previous_stage = st.session_state.stage # Store current stage
    st.session_state.stage = "phrases"



def reset_flow() -> None:
    st.session_state.stage = "intro"
    st.session_state.selected_category = None
    st.session_state.options = []
    st.session_state.last_phrase = None
    st.session_state.audio_file = None
    st.session_state.play_triggered = False
    st.session_state.text_input_value = ""
    st.session_state.predicted_phrase = None
    st.session_state.predicted_audio_file = None
    st.session_state.phrase_predicted = False
    st.session_state.play_count = 0



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
            st.session_state.previous_stage = st.session_state.stage # Store current stage
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
                st.session_state.previous_stage = st.session_state.stage # Store current stage
                st.session_state.stage = "loading"
                st.rerun()

    if st.button(f'← {TEXT["back_to_intro"]}', key="back_intro", use_container_width=True):
        reset_flow()
        st.rerun()

    st.markdown("---") # Separator for text input button
    if st.button(f'📝 {TEXT["or_type_something"]}', key="type_something_btn", use_container_width=True):
        st.session_state.previous_stage = st.session_state.stage # Store current stage
        st.session_state.stage = "text_input_stage"
        st.rerun()

def render_phrase_options() -> None:
    st.markdown(f"## {TEXT['tap_sentence_title']}")

    for option in st.session_state.options:

        label = (
            option["emoji"]
            if st.session_state.emoji_only
            else f"{option['emoji']}  {option['text']}"
        )

        if st.button(
            label,
            key=f"phrase_{option['id']}",
            use_container_width=True
        ):
            text = option["text"]

            # Generate audio
            audio_file = synthesize_audio(text, LANG)

            # 🔊 PLAY IMMEDIATELY
            if audio_file:
                st.audio(audio_file, autoplay=True)

            # Store last phrase (still useful)
            st.session_state.last_phrase = text

            # Notify parent
            notifier.send_notification(CHILD_ID, text)

            # Store in Qdrant (unchanged)
            try:
                if st.session_state.get("qdrant_initialized"):
                    qdrant_manager.store_phrase(
                        child_id=CHILD_ID,
                        category=st.session_state.selected_category,
                        phrase=text,
                        context=build_context(st.session_state.selected_category),
                    )
            except Exception:
                pass

            # Storing last phrase, notifying parent, and storing in Qdrant will still occur.

            # We explicitly do NOT change the stage to "voice" and do NOT call st.rerun()
            # to keep the user on the current phrase options page after audio plays.
            # This addresses the bug where pressing a button leads to a new page.

    
    st.markdown("---")
    if st.button(TEXT["show_more_options"], key="show_more_options_btn", use_container_width=True):
        st.session_state.previous_stage = st.session_state.stage # Store current stage
        st.session_state.stage = "loading"
        st.rerun()

    if st.button(TEXT["back_to_categories"], use_container_width=True):
        st.session_state.previous_stage = st.session_state.stage # Store current stage
        st.session_state.stage = "categories"
        st.rerun()

    

def render_voice_output() -> None:
    if not st.session_state.last_phrase:
        st.session_state.stage = "phrases"
        st.rerun()
        return
        
    st.markdown(f"""
    <div class="card play-card">
        <span class="badge">{TEXT["stage_4_badge"]}</span>
        <div class="play-icon">🔊</div>
        <p class="play-phrase">{st.session_state.last_phrase}</p>
        <p class="hint">{TEXT["voice_card_body"]}</p>
    </div>
    """.format(
        stage_4_badge=TEXT["stage_4_badge"],
        last_phrase=st.session_state.last_phrase,
        voice_card_body=TEXT["voice_card_body"]
    ), unsafe_allow_html=True)

    if st.session_state.audio_file and not st.session_state.play_triggered:
        st.audio(st.session_state.audio_file, autoplay=True)
        st.session_state.play_triggered = True
    
    col1, col2 = st.columns(2)

    with col1:
        # "Play Again" button with an emoji and full width.
        # Styling applied via CSS targeting "stButton-play_again_btn".
        if st.button(f'▶ {TEXT["play_again"]}', key="play_again_btn", use_container_width=True):
            st.session_state.play_triggered = False # Reset flag to allow replay
            st.rerun()
    if st.button(f'🏠 {TEXT["start_over"]}', key="start_over_btn", use_container_width=True):
        reset_flow()
        st.rerun()

    # Back button
    if st.session_state.previous_stage in ["phrases", "text_input_stage"]:
        if st.button(f'← {TEXT["back_to_categories"]}', key="back_from_voice", use_container_width=True):
            st.session_state.stage = st.session_state.previous_stage
            st.rerun()


def render_text_input_stage() -> None:
    # ⬅ Back button (must be at the top)
    if st.button("⬅ Back", use_container_width=True):
        st.session_state.stage = st.session_state.get("previous_stage", "home")
        st.rerun()

    st.markdown(f"## {TEXT['say_something_title']}")

    # Input box
    typed_text = st.text_input(
        label=TEXT["type_phrase_label"],
        value=st.session_state.text_input_value,
        key="text_input_box",
        help=TEXT["type_phrase_help"]
    )

    st.session_state.text_input_value = typed_text
    st.session_state.play_triggered = False

    # Predict button
    if st.button(
        TEXT["predict_phrase_button"],
        key="predict_button",
        use_container_width=True,
        type="primary"
    ):
        if st.session_state.text_input_value:
            with st.spinner("Thinking..."):
                predicted = predict_intent(
                    st.session_state.text_input_value,
                    LANG
                )

                text = predicted["text"]
                emoji = predicted["emoji"]

                # 🔊 Audio
                audio_file = synthesize_audio(text, LANG)
                if audio_file:
                    st.audio(audio_file, autoplay=True)

                # Save state
                st.session_state.last_phrase = text
                st.session_state.predicted_phrase = f"{emoji} {text}"

                # Notify parent
                notifier.send_notification(CHILD_ID, text)

                # Store stage history
                st.session_state.previous_stage = st.session_state.stage
                st.session_state.stage = "voice"
                st.rerun()
        else:
            st.warning(TEXT["empty_text_input_warning"])



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
    elif stage == "text_input_stage": # New stage for text input
        render_text_input_stage()
    elif stage == "voice":
        render_voice_output()

if __name__ == "__main__":
    main()