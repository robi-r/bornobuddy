# BornoBuddy (বর্ণবন্ধু) – Assistive AI Communication Tool
# Visit the app by following this url: https://bornobuddy.streamlit.app/

BornoBuddy is an innovative, AI-powered communication tool designed for **non-verbal or minimally verbal autistic children in Bangladesh**. It empowers children to express their needs and feelings through a simple, visual, and culturally adapted interface.

## 🚀 Live Demo

Experience BornoBuddy in action! [Visit the App](https://bornobuddy.streamlit.app/)

## ✨ Features

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

---

## 🛠️ Technology Stack

*   **Language**: Python
*   **Framework**: Streamlit (for interactive web application)
*   **AI Engine**: Google Gemini (for context-aware phrase generation)
*   **Text-to-Speech (TTS)**: gTTS (Google Text-to-Speech for natural Bengali voice output)
*   **Personalization**: Qdrant (Vector Database for storing and retrieving user phrases, enabling adaptive suggestions)
*   **Configuration**: `python-dotenv` (for managing environment variables)

---

## 🚀 Getting Started

Follow these steps to set up and run BornoBuddy locally:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/robi-r/bornobuddy.git
    cd BornoBuddy
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the project's root directory and add your Google Gemini API key:

    ```
    GEMINI_API_KEY="your_gemini_api_key_here"
    # Optional: Specify your Gemini model. Defaults to 'gemini-pro'.
    # GEMINI_MODEL="gemini-1.5-flash"
    ```

    Ensure Qdrant is initialized for personalization. This happens automatically when the app runs, creating a local vector store in `qdrant_storage/`.

4.  **Run the application:**

    ```bash
    streamlit run app.py
    ```

    Your browser will automatically open to the Streamlit app.

---

## 💡 Future Enhancements

We welcome contributions and suggestions for improving BornoBuddy! Here are some ideas:

*   **Culturally Specific Categories:** Expand with more categories relevant to Bangladeshi culture, such as "Family & Home" (পরিবার ও বাড়ি), "Festivals & Games" (উৎসব ও খেলা), and more specific food items under "Food & Drink" (খাবার ও পানীয়).
*   **Localized Imagery:** Replace generic emojis with custom icons or drawings that reflect Bangladeshi culture (e.g., a mango instead of an apple, a cricket bat for activities).
*   **Offline Mode:** Implement a fallback mechanism to suggest common phrases from a pre-saved list when an internet connection is unavailable.
*   **Voice Customization:** Allow users to choose between different voices (e.g., male, female, child) for a more personalized experience.
*   **User Management:** Implement user authentication and profiles to save individual personalization settings and usage history.
*   **Admin Dashboard:** Develop a dashboard for administrators to manage phrases, categories, and monitor app usage.

---