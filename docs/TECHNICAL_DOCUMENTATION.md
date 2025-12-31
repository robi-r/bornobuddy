# BornoBuddy Technical Documentation

## 1. Introduction

BornoBuddy (বর্ণবন্ধু) is an assistive AI communication tool specifically designed for non-verbal or minimally verbal autistic children in Bangladesh. It aims to empower children to express their needs and feelings through a simple, visual, and culturally adapted interface. This document provides a detailed technical overview of the project, its architecture, key components, and implementation details.

## 2. System Architecture

BornoBuddy is built as a Streamlit web application, leveraging several key technologies for its functionality:

*   **Frontend & Application Logic (Streamlit):** Streamlit serves as the primary framework for building the user interface and handling the application's core logic and state management. Its component-based nature allows for rapid development and interactive UIs.
*   **AI Phrase Generation (Google Gemini):** The application integrates with the Google Gemini model (configurable via `GEMINI_MODEL`) to generate context-aware phrases. This is crucial for providing relevant and personalized communication options to the child.
*   **Text-to-Speech (gTTS):** Google Text-to-Speech (gTTS) is used to convert the generated Bengali phrases into natural-sounding audio, which the application then plays aloud.
*   **Personalization (Qdrant Vector Database):** Qdrant is employed as a local vector database to store and retrieve previously selected user phrases. This enables a personalization feature where the AI's suggestions can be influenced by the child's past communication patterns.
*   **Environment Management (`python-dotenv`):** Sensitive information, such as the `GEMINI_API_KEY`, and configurable parameters like `GEMINI_MODEL`, are managed using `python-dotenv`, ensuring secure and flexible configuration.

The overall data flow involves:
1.  User interaction (e.g., selecting a category) updates the Streamlit session state.
2.  Contextual information (category, time, location, last phrase, personalization data from Qdrant) is gathered.
3.  This context is used to formulate a prompt for the Google Gemini model.
4.  Gemini generates three suggested phrases.
5.  The selected phrase is converted to audio via gTTS.
6.  The audio is played, and the phrase is optionally stored in Qdrant for future personalization.

## 3. Key Modules and Files

### `app.py` (Main Application Logic)

This is the core of the BornoBuddy application. It orchestrates the entire user experience and integrates all other components.

*   **`TRANSLATIONS` Dictionary:** Manages all application texts in Bengali (`bn`) and English (`en`), enabling seamless language switching.
*   **`CATEGORY_CONFIGS`:** Defines the available communication categories and their associated emojis for both languages.
*   **`init_session_state()`:** Initializes Streamlit's `st.session_state` variables, managing the application's stage, selected options, audio files, and other dynamic data.
*   **`inject_custom_css()`:** Dynamically injects custom CSS into the Streamlit app to control the overall aesthetic, color palette, typography, and responsive behavior for a child-friendly design.
*   **`render_header()`:** Renders the application header, including the app title, subtitle, and language toggle button. It also displays a visual progress indicator.
*   **`build_context()`:** Gathers real-time contextual information (date, time, location, last spoken phrase) to inform the AI model's phrase generation, making suggestions more relevant.
*   **`load_prompt_template()`:** Loads the prompt template for the Gemini model from the `prompts/` directory, allowing for language-specific and customizable prompts.
*   **`parse_model_output()`:** Processes the raw text response from the Gemini model, extracting and validating the generated phrases and their emojis into a structured format.
*   **`generate_ai_options()`:** The central function for AI interaction. It builds the full prompt context (including personalization data from Qdrant), calls the Gemini API, and returns the parsed phrase suggestions.
*   **`fetch_options()`:** Manages the state transition to "loading" while AI options are being generated and then to "phrases" once available.
*   **`synthesize_audio()`:** Utilizes gTTS to convert text into an MP3 audio file. This function is decorated with `@st.cache_data` to cache previously generated audio, improving performance and reliability.
*   **`reset_flow()`:** Resets the application's session state to return to the initial "intro" stage.
*   **UI Stage Renderers (`render_stage_intro()`, `render_categories()`, `render_phrase_options()`, `render_voice_output()`):** These functions are responsible for rendering specific sections of the UI based on the current `st.session_state.stage`. They handle button interactions, display dynamic content, and manage stage transitions.
*   **`main()`:** The entry point of the Streamlit application, initializing Qdrant (if not already), rendering the header, and then calling the appropriate UI stage renderer based on `st.session_state.stage`.

### `qdrant_manager.py` (Qdrant Integration)

This module handles all interactions with the Qdrant vector database for personalization.

*   **`init_qdrant()`:** Initializes the Qdrant client, connects to the local Qdrant instance, and ensures the necessary collection (`echomind_phrases`) exists.
*   **`store_phrase()`:** Stores a child's selected phrase along with its context (category, time, location) into the Qdrant vector database. This data is vectorized (though the vectorization logic isn't explicitly shown in `app.py`, it's an implicit part of `qdrant_manager`).
*   **`get_personalization_context()`:** Queries Qdrant to retrieve past phrases and context relevant to the current situation, which is then fed back to the Gemini model to influence new suggestions.

### `prompts/` (Prompt Templates)

This directory contains plain text files that serve as templates for the prompts sent to the Google Gemini model.

*   `suggestion_prompt_bn.txt`: Bengali prompt template.
*   `suggestion_prompt_en.txt`: English prompt template.

These templates allow for flexible and language-specific instructions to the AI model. The `build_context()` function dynamically inserts real-time information into these templates.

## 4. Data Flow

1.  **Start (Intro Page):** User clicks "I want to speak" button.
2.  **Category Selection:** User chooses a category.
3.  **Loading Phrases:**
    *   `build_context()` gathers real-time data.
    *   `qdrant_manager.get_personalization_context()` fetches relevant past interactions.
    *   `load_prompt_template()` gets the AI prompt base.
    *   `generate_ai_options()` constructs the full prompt, calls Gemini, and gets raw AI suggestions.
    *   `parse_model_output()` processes Gemini's response into structured phrases.
    *   `st.session_state.options` is updated with new phrases.
4.  **Phrase Options Display:** User selects a phrase.
5.  **Voice Output:**
    *   `synthesize_audio()` converts the selected phrase to an MP3.
    *   `st.audio()` plays the MP3.
    *   `qdrant_manager.store_phrase()` saves the selected phrase and context for future personalization.
6.  **Replay/Reset:** User can replay the audio or start the flow over.

## 5. Session State Management

Streamlit's `st.session_state` is extensively used to maintain the application's state across reruns. Key variables include:

*   **`stage`**: Current stage of the application flow (`"intro"`, `"categories"`, `"loading"`, `"phrases"`, `"voice"`).
*   **`selected_category`**: The category chosen by the user.
*   **`latitude`, `longitude`, `location_name`**: User's geographical location data (if available).
*   **`gps_requested`**: Flag to track if GPS permission was requested.
*   **`options`**: List of AI-generated phrase suggestions.
*   **`last_phrase`**: The last phrase spoken by the application.
*   **`audio_file`**: Path to the temporary MP3 audio file.
*   **`play_triggered`**: Flag to control initial audio autoplay and prevent multiple replays on subsequent reruns.
*   **`language`**: Current language of the application (`"bn"` or `"en"`).
*   **`qdrant_initialized`**: Flag to indicate if Qdrant has been successfully initialized.

## 6. Custom CSS (`inject_custom_css`)

The `inject_custom_css()` function customizes the Streamlit UI for a child-friendly, modern, and clean aesthetic. It defines:

*   **Color Palette (`:root` variables):** Uses a harmonious set of pastel colors with cheerful accents for a vibrant yet gentle look.
*   **Typography:** Specifies `Fredoka One` (playful) for headings and `Open Sans` (readable) for body text, with adjusted font sizes for clarity.
*   **Spacing & Layout:** Employs generous padding, margins, and `gap` properties to create an uncluttered and easy-to-navigate interface.
*   **Rounded Elements:** Utilizes large `border-radius` values (e.g., `var(--radius-lg)`, `var(--radius-full)`) for a softer, more approachable feel.
*   **Subtle Shadows:** Applies `box-shadow` for depth without being distracting.
*   **Interactive Element Styling:** Provides custom styles for various buttons (`.stButton > button`, `primary-btn`, `[data-testid*="stButton-phrase_"] button`, etc.) including hover and active states, to make them visually responsive and engaging.
*   **Voice Output Card Styling:** Dedicated CSS for `.card.play-card`, `.play-card .play-icon`, and `.play-card .play-phrase` ensures the voice output is prominently and aesthetically presented.

## 7. Error Handling

The application implements error handling at various critical points:

*   **Gemini API Errors:** Catches exceptions during Gemini API calls (`generate_ai_options`) and displays user-friendly error messages (`st.error`) with suggestions (e.g., checking API key, model name).
*   **Gemini Response Parsing Errors:** Handles `json.JSONDecodeError` and `ValueError` if Gemini's response is not in the expected JSON format or does not contain the correct number of phrases, guiding the user to ensure valid AI output.
*   **Qdrant Initialization Warnings:** Catches exceptions during `qdrant_manager.init_qdrant()` and issues a warning (`st.warning`), allowing the app to run without personalization if Qdrant setup fails.
*   **Audio Generation Warnings:** Catches exceptions during `gTTS` usage (`synthesize_audio`) and displays a warning (`st.warning`) if audio cannot be generated.

## 8. Localization (`TRANSLATIONS`)

The application supports dual languages (Bengali and English) through the `TRANSLATIONS` dictionary.

*   All user-facing strings are stored in this dictionary, keyed by language code (`"bn"`, `"en"`).
*   The `st.session_state.language` variable controls the currently active language.
*   A language toggle button in the header allows users to switch languages dynamically, triggering an `st.rerun()` to update the UI.
*   Prompt templates for the Gemini model are also loaded based on the selected language.

## 9. Deployment Considerations

BornoBuddy is designed for deployment on Streamlit Cloud, which offers a straightforward deployment process.

*   **GitHub Repository:** The project is hosted on GitHub, which Streamlit Cloud directly integrates with for deployment.
*   **.env File:** The `.env` file containing `GEMINI_API_KEY` and `GEMINI_MODEL` (if specified) should *not* be committed to the public repository. Streamlit Cloud allows you to configure these as "Secrets" in its deployment settings, ensuring secure handling of sensitive credentials.
*   **`requirements.txt`:** All Python dependencies are listed in `requirements.txt`, which Streamlit Cloud uses to set up the deployment environment.
*   **Main File Path:** `app.py` should be specified as the main file for the Streamlit application.
