# BornoBuddy Technical Documentation

## Overview

### Problem Statement

Communication challenges faced by non-verbal or minimally verbal autistic children are significant. These children often struggle to express their basic needs, feelings, and desires, leading to frustration, behavioral issues, and limited social interaction. Existing assistive communication tools may lack cultural relevance, be overly complex, or not adapt to individual needs, especially in contexts like Bangladesh where localized solutions are scarce.

### Target Users

The primary target users are:
*   **Non-verbal or minimally verbal autistic children (ages 3-12)** in Bangladesh.
*   Their **parents, caregivers, and special education teachers** who support their communication development.

### Why the Problem Matters (Local + Scalable Impact)

**Local Impact (Bangladesh):**
*   **Empowerment:** Provides a voice to children who otherwise struggle to communicate, fostering self-expression and reducing frustration.
*   **Enhanced Care:** Enables caregivers to better understand and respond to the child's needs, improving daily interactions and overall well-being.
*   **Educational Support:** Facilitates learning and participation in educational settings by offering a structured communication method.
*   **Cultural Relevance:** Addresses a gap in the market for culturally and linguistically appropriate assistive technology in Bangladesh.

**Scalable Impact:**
*   **Model for Localized AT:** BornoBuddy can serve as a successful model for developing assistive technology tailored to specific cultural and linguistic contexts worldwide.
*   **Community Building:** Fosters a more inclusive society by supporting the integration of autistic children.
*   **Research & Development:** The personalization data collected (anonymously) can contribute to further research in personalized assistive communication.
*   **Accessibility:** Improves accessibility to communication tools in low-resource settings by leveraging readily available technologies (smartphones, web apps).

---

## Solution Description

### What We Built

BornoBuddy is a Streamlit-based web application that functions as an assistive AI communication tool. It simplifies communication for non-verbal autistic children by guiding them through a 4-step process: initiating communication, selecting a category, receiving AI-generated phrase suggestions, and playing selected phrases aloud. The application is designed to be intuitive, culturally relevant, and adaptable through personalization.

### Core Features

BornoBuddy is built with clinical best practices for children with verbal impairments and autism, focusing on a low-effort, high-impact communication experience:

*   **Simple 4-Step Communication Flow:**
    1.  **Start:** The child taps a large, inviting button to indicate **“আমি বলতে চাই”** (I want to speak).
    2.  **Choose Category:** They select from **four clear, visual categories** relevant to a child's daily life in Bangladesh.
    3.  **Get Suggestions:** Powered by Google Gemini, the system generates **three simple, context-aware phrases in Bengali**, each paired with a clear emoji.
    4.  **Speak Aloud:** The child taps a phrase, and the device **speaks it out loud in a natural Bengali voice**.
*   **Dual Language Support:** Instantly switch between **Bengali (বাংলা)** and **English** with a single tap, catering to bilingual families and diverse educational settings.
*   **Intuitive & Predictable UI:**
    *   **Visual Progress Indicator:** A clear progress bar shows the child their current step in the 4-step process, reducing anxiety and making interaction predictable.
    *   **Reduced Clutter:** The interface is streamlined, removing non-essential text and visuals to help children focus on communication.
*   **User-Controlled Audio:** The app empowers children with full control; they tap a "Play" button to hear phrases, preventing sensory overload.
*   **Culturally-Aware Design:** Features a color scheme inspired by the Bangladeshi flag and defaults to Bengali, offering a welcoming and familiar experience for children in Bangladesh.
*   **AI-Powered Personalization:** Utilizes Qdrant (Vector Database) to store and retrieve user phrases, enabling personalized phrase suggestions over time.
*   **Parent Notification:** Automatically sends an email notification to a configured parent email address when a child selects a phrase, providing real-time awareness of the child's communication.
*   **Text Input with AI Prediction:** Allows children or caregivers to type a phrase, which is then rephrased into a simple, literal statement with an emoji by Google Gemini, and can be spoken aloud.

### User Journey / Flow

The typical user journey through BornoBuddy is a simplified 4-step process:

1.  **Initiation (Intro Stage):**
    *   The child sees a welcoming intro screen with a large "I want to speak" button.
    *   They tap this button to begin their communication.
2.  **Category Selection (Categories Stage):**
    *   Presented with four clear, visual categories (e.g., Body & Needs, Feelings & Sensory).
    *   The child taps on a category that best represents what they want to communicate about.
3.  **Phrase Suggestion (Loading & Phrases Stage):**
    *   A brief "Loading phrases..." spinner appears while the AI (Google Gemini) generates suggestions based on the chosen category and personalized context (from Qdrant).
    *   Three context-aware phrases, each with a relevant emoji, are displayed.
    *   The child can tap "Show More Options" to get a new set of suggestions or "Back to Categories" to choose a different topic.
4.  **Voice Output (Voice Stage):**
    *   Upon selecting a phrase, the phrase is prominently displayed.
    *   A "Play Again" button allows the child to hear the phrase spoken aloud (using gTTS).
    *   A "Start Over" button allows them to return to the intro screen.
    *   The selected phrase is stored in Qdrant for future personalization.

---

## AI & System Architecture

### Models Used

*   **Google Gemini (via `google.genai`):** Utilized for generating dynamic, context-aware phrase suggestions and for **AI-powered intent prediction** from text input. The specific model is configurable via the `GEMINI_MODEL` environment variable (e.g., `gemini-pro`, `gemini-1.5-flash`). The model is chosen for its natural language generation capabilities and ability to generate structured JSON output.
*   **gTTS (Google Text-to-Speech):** Used for converting Bengali text into natural-sounding speech. This is an external library that interacts with Google's TTS service.

### RAG / Agents / Automation

*   **Retrieval-Augmented Generation (RAG):** BornoBuddy implements a form of RAG through its personalization feature. The Qdrant vector database acts as the "retrieval" component, storing a history of the child's selected phrases and their contexts. When generating new suggestions, this historical data is "augmented" into the prompt for the Gemini model, allowing Gemini (the "generation" component) to produce more personalized and relevant output.
*   **Agents / Automation:** While BornoBuddy does not currently utilize complex multi-agent systems, the interaction flow is automated. The AI (Gemini) acts as a generative agent responding to prompts, and the overall application flow manages user interaction and state transitions automatically. There's potential for future integration with more sophisticated agentic workflows.

### Data Flow and Decision Logic

(See Section 2. System Architecture for a high-level data flow diagram. This section elaborates on the decision logic.)

*   **Initialization:** Upon app launch, `init_session_state()` sets default UI stage and clears previous state. `qdrant_manager.init_qdrant()` attempts to connect to Qdrant.
*   **Navigation:**
    *   User actions (button clicks) update `st.session_state.stage`.
    *   `st.rerun()` is called to re-execute the script, leading to the rendering of the UI corresponding to the new `stage`.
*   **Phrase Generation Logic (`generate_ai_options`):**
    1.  **Context Building:** `build_context()` gathers current app state, date/time, and (if available) location.
    2.  **Personalization Retrieval:** If Qdrant is initialized, `qdrant_manager.get_personalization_context()` is called to retrieve past relevant phrases.
    3.  **Prompt Construction:** `load_prompt_template()` retrieves the base prompt, and the gathered context (including personalization) is formatted into it.
    4.  **Gemini Call:** The constructed prompt is sent to the Gemini model.
    5.  **Output Parsing:** `parse_model_output()` validates Gemini's JSON response, ensuring it contains exactly three phrases with associated text and emoji. If invalid, an error is displayed.
*   **Audio Playback Logic:**
    1.  Upon phrase selection, `synthesize_audio()` (cached via `@st.cache_data`) generates or retrieves the MP3.
    2.  The `st.audio()` component is rendered.
    3.  Initial playback is controlled by `st.session_state.play_triggered`.
    4.  The "Play Again" button resets `st.session_state.play_triggered` to `False` and triggers `st.rerun()`, forcing a re-evaluation of the `st.audio` component and re-playback.
*   **Error Handling:** Specific `try-except` blocks are used around Gemini API calls, JSON parsing, and audio generation to gracefully handle errors and provide informative feedback to the user via `st.error` or `st.warning`.
*   **Parent Notification Logic:**
    1.  Upon phrase selection in `render_phrase_options`, the `notifier.send_notification()` function is called.
    2.  This function retrieves `APP_EMAIL`, `APP_EMAIL_PASSWORD`, and `PARENT_EMAIL` from environment variables.
    3.  It constructs an email with the child's ID and the selected phrase.
    4.  Using `smtplib`, the email is sent to the `PARENT_EMAIL` address. Graceful error handling is implemented to prevent app crashes if email sending fails.
*   **Text Input and AI Prediction Logic:**
    1.  When the user navigates to the `text_input_stage`, a Streamlit `text_input` field is displayed.
    2.  Upon clicking the "Predict Phrase with AI" button, the `predict_intent()` function is called with the typed text and current language.
    3.  `predict_intent()` loads a specific prompt template (`predict_intent_prompt_{language}.txt`).
    4.  It constructs a prompt that includes the user's input and sends it to the Gemini model.
    5.  The model's JSON response (containing a predicted phrase and emoji) is parsed.
    6.  The predicted phrase is then set as `st.session_state.last_phrase` and its audio is synthesized, leading to the `voice` stage for playback.

---

## Prompt & Process Documentation

### Prompts Used

#### 1. Ideation and Problem Framing

*   **Context:** Initial phase of understanding the challenge of communication for non-verbal autistic children, especially in a culturally specific context like Bangladesh.
*   **Prompts:**
    *   "What are the primary communication challenges for non-verbal autistic children, particularly in non-Western cultures?"
    *   "How can AI be leveraged to create an intuitive and accessible communication tool for children with limited verbal abilities?"
    *   "What cultural considerations are crucial when designing assistive technology for children in Bangladesh?"
    *   "Brainstorm initial feature sets for a simple 4-step communication app targeting autistic children."

#### 2. Architecture and System Design

*   **Context:** Designing the technical backbone of BornoBuddy, selecting appropriate technologies, and defining component interactions.
*   **Prompts:**
    *   "Design a scalable and maintainable architecture for a Streamlit-based assistive communication app using Google Gemini for phrase generation. Consider personalization and multilingual support."
    *   "How can Qdrant be integrated to provide personalized AI suggestions based on past user interactions in a Streamlit app?"
    *   "What are the best practices for managing session state and UI transitions in a Streamlit application that requires a predictable user flow?"
    *   "Propose a robust error handling strategy for a Streamlit app integrating external APIs (Gemini, gTTS) and a local database (Qdrant)."

#### 3. Coding or Agent Workflows (Agentic Loop for Development)

*   **Context:** This documentation itself is being generated through an agentic workflow. The agent (me) uses prompts to understand requests, plan, implement, and refine code.
*   **Prompts (Internal Agent Prompts during development, for example):**
    *   "Read `app.py` and identify potential UI errors or areas for improvement in rendering or user experience."
    *   "Fix the audio replay functionality in `render_voice_output` without using the `key` argument, as it's not supported in the current Streamlit version. Ensure smooth re-playback on button click."
    *   "Overhaul the Streamlit UI to be more clean, modern, and child-friendly. This includes adjusting color palette, typography, spacing, shadows, and button styles within `inject_custom_css`."
    *   "Generate comprehensive technical documentation for the BornoBuddy project, covering architecture, data flow, key modules, and deployment considerations, adhering to a specified structure."

#### 4. Evaluation and Reasoning

*   **Context:** Assessing the effectiveness of implemented features, identifying bugs, and making decisions based on trade-offs.
*   **Prompts:**
    *   "Analyze the current implementation of category selection in `render_categories`. Suggest a more idiomatic Streamlit approach to avoid complex HTML/JS and potential UI errors."
    *   "Review the audio playback mechanism in `render_voice_output`. Propose a robust solution for replaying audio on demand, considering Streamlit's rerunning model and potential limitations."
    *   "Evaluate the overall child-friendliness and engagement of the Intro page. Suggest concrete improvements for visual appeal and interactivity."

### Explanation of How Prompts Influenced Outputs

The prompts served as direct instructions and contextual information, guiding the development process at every stage. For instance:
*   **Problem Framing prompts** helped in understanding the project's core mission and the unique challenges faced by the target audience, leading to design decisions focused on simplicity, predictability, and cultural relevance.
*   **Architecture prompts** directly influenced the choice of technologies (Streamlit, Gemini, Qdrant) and the conceptual design of how these components would interact, prioritizing features like personalization and multilingual support.
*   **Coding/Agent Workflow prompts** translated directly into actionable tasks, leading to the implementation of specific code changes for UI enhancements, bug fixes (like the audio replay), and feature additions (e.g., "Show More Options" button). The iterative nature of these prompts allowed for continuous refinement.
*   **Evaluation prompts** facilitated self-correction and improvement. When a UI element was identified as problematic or an audio feature was reported as buggy, specific prompts guided the analysis of the issue and the formulation of targeted solutions.

The iterative dialogue, driven by these prompts, allowed for a systematic approach to development, ensuring that the output (the BornoBuddy application and its documentation) evolved in response to explicit requirements and identified areas for improvement.

---
### Problem

(Refer to the "Problem Statement" in the Overview section for detailed content.)
*   Difficulty for non-verbal autistic children to communicate their needs and feelings.
*   Lack of culturally relevant and adaptable assistive communication tools in regions like Bangladesh.
*   Frustration for both children and caregivers due to communication barriers.

### Solution

(Refer to the "Solution Description" in the Overview section for detailed content.)
*   BornoBuddy: A Streamlit-based AI communication tool.
*   Simple 4-step visual interface.
*   AI-generated (Gemini) context-aware and personalized phrases.
*   Text-to-speech (gTTS) in natural Bengali voice.
*   Dual language support (Bengali/English).

### Demo Flow

(This would typically involve screenshots or a live walkthrough, but text outlines the user journey.)
*   Child taps "I want to speak" on Intro screen.
*   Chooses a category (e.g., Body & Needs).
*   Sees three AI-suggested phrases with emojis.
*   Taps a phrase.
*   Hears the phrase spoken aloud, can replay or start over.

### Architecture

(Refer to the "AI & System Architecture" section for detailed content.)
*   Streamlit Frontend & State Management.
*   Google Gemini for AI.
*   gTTS for Text-to-Speech.
*   Qdrant for personalization (RAG).
*   GitHub for version control/deployment.

### Impact and Scalability

(Refer to "Why the Problem Matters" in the Overview section for detailed content.)
*   **Impact:** Empowers children, improves care, supports education, culturally relevant.
*   **Scalability:** Model for localized AT, community integration, research data, broader accessibility.

## Product Roadmap

### MVP Scope (Current Implementation)

*   **Core Communication Flow:** 4-step process (Start, Category, Suggestion, Voice Output).
*   **Dual Language Support:** Bengali and English.
*   **AI Phrase Generation:** Google Gemini integration for context-aware suggestions.
*   **Text-to-Speech:** gTTS for Bengali audio output.
*   **Basic Personalization:** Qdrant integration to store and retrieve past user phrases.
*   **Child-Friendly UI:** Clean, modern, intuitive design with a specific color palette.
*   **Error Handling:** Robust error management for API calls, parsing, and audio generation.
*   **Email Configuration:** Integration of environment variables (`APP_EMAIL`, `APP_EMAIL_PASSWORD`, `PARENT_EMAIL`) for secure email notification setup.
*   **Prompt Templates for Intent Prediction:** Dedicated `.txt` files (`predict_intent_prompt_bn.txt`, `predict_intent_prompt_en.txt`) defining the Gemini model's behavior for rephrasing user text input.
*   **Deployment Ready:** Configured for Streamlit Cloud deployment.

### Innovations Implemented

*   **Culturally Adapted AI Communication:** Tailored for a specific linguistic and cultural context (Bangladesh/Bengali).
*   **Email Notification for Caregivers:** Implemented real-time email notifications to parents/caregivers upon phrase selection, increasing awareness and support.
*   **Text Input with AI-powered Intent Prediction:** Introduced a feature allowing direct text input from which AI interprets and refines the child's intended message into a clear, speakable phrase.
*   **Personalized Phrase Suggestions:** Leveraging Qdrant for Retrieval-Augmented Generation to make AI output more relevant over time.
*   **Predictable & Low-Cognitive Load UI:** Designed with non-verbal autistic children in mind, focusing on simplicity, visual cues, and controlled interaction.
*   **On-Device Customization:** Qdrant runs locally, ensuring privacy and responsiveness for personalization.

### Next-Phase Roadmap and Scaling Plan

*   **Enhanced Personalization:**
    *   Implement more sophisticated personalization algorithms beyond simple retrieval (e.g., preference learning, adaptive models).
    *   Allow caregivers to "teach" the app new phrases or adjust existing ones.
*   **Expanded Categories & Content:**
    *   Add more granular categories and a wider vocabulary of phrases.
    *   Incorporate support for more complex sentence structures.
*   **Customizable Visuals:**
    *   Allow users to upload custom images for categories or phrases.
    *   Offer different UI themes and accessibility options.
*   **Offline Functionality:**
    *   Develop a mechanism for the app to function with limited internet connectivity, leveraging pre-cached phrases.
*   **Multi-Platform Support:**
    *   Explore native mobile app development (Android/iOS) or desktop versions for broader accessibility.
*   **Analytics & Insights (Privacy-Preserving):**
    *   Develop features for caregivers to gain insights into communication patterns, while strictly adhering to privacy protocols.
*   **Community Features:**
    *   Enable sharing of phrase sets or personalized profiles among trusted users/caregivers.
*   **Integration with Wearables/Sensors:**
    *   Future possibility to integrate with external sensors for context (e.g., heart rate for emotional state, environmental factors).

---

## About This Documentation

This documentation was generated as part of an agentic development workflow. The sections related to "Prompt & Process Documentation" reflect the iterative interaction and decision-making process guided by explicit prompts.

---

## Deployment & Access

**Public Access:**
This documentation is intended to be publicly accessible with viewer permissions. When hosting this document (e.g., on GitHub Pages, Google Docs, etc.), ensure that the access settings allow anyone with the link to view the content.
