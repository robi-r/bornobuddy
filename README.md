# BornoBuddy (বর্ণবন্ধু) – An Assistive AI Communication Tool for Verbally Impaired autistic Children in Bangladesh
# Visit the app by following this url:https://bornobuddy.streamlit.app/

**BornoBuddy (বর্ণবন্ধু)** is a simple, visual, AI-powered communication tool designed for **non-verbal or minimally verbal autistic children in Bangladesh**.

The core idea is to provide a low-effort, high-impact communication experience:


1.  The child taps a large, inviting button to indicate **“আমি বলতে চাই”** (I want to speak).
2.  They choose from **four clear, visual categories** relevant to a child's daily life in Bangladesh.
3.  The system, powered by Google Gemini, generates **three simple, context-aware phrases in Bengali**, each paired with a clear emoji.
4.  The child taps a phrase, and the device **speaks it out loud in a natural Bengali voice**.

This approach minimizes cognitive load, making it easier for children to express their needs and feelings, thereby giving them a greater sense of agency.

## Key Features (Doctor's Improvements)

This version of BornoBuddy has been enhanced with features specifically designed for children with verbal impairments and autism, based on clinical best practices:

*   **Dual Language Support:** Users can instantly switch between **Bengali (বাংলা)** and **English** with a single tap, making the app versatile for bilingual families and different educational settings.
*   **Simplified, Predictable UI:**
    *   **Progress Indicator:** A visual progress bar shows the child which step they are on in the 4-step process, reducing anxiety and making the interaction predictable.
    *   **Reduced Clutter:** The interface has been streamlined to remove all non-essential text and visuals, helping the child focus on the communication task.
*   **Enhanced Sensory Control:**
    *   **User-Controlled Audio:** The app no longer plays audio automatically. The child has full control and can tap a "Play" button to hear the phrase, which helps prevent sensory overload.
*   **Culturally-Aware Design:** The app uses a color scheme inspired by the Bangladeshi flag, and the default language is Bengali, ensuring it is welcoming and familiar to children in Bangladesh.

---

## 🛠️ Technology Stack

*   **Language**: Python
*   **Frontend & Logic**: Streamlit
*   **AI Phrase Generation**: Google Gemini
*   **Text-to-Speech (TTS)**: gTTS (Google Text-to-Speech)
*   **Personalization**: Qdrant (Vector Database for storing and retrieving user phrases)
*   **Environment Management**: `python-dotenv`

---

## 🚀 Getting Started

1.  **Clone the repository and install dependencies:**

    ```bash
    git clone <https://github.com/robi-r/bornobuddy.git>
    cd BornoBuddy
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**

    Create a `.env` file in the project's root directory and add your Gemini API key:

    ```
    GEMINI_API_KEY="your_gemini_api_key_here"
    GEMINI_MODEL="gemini-1.5-flash"
    ```

3.  **Run the application:**

    ```bash
    streamlit run app.py
    ```

---

## 💡 Suggestions for Future Improvements

*   **Culturally Specific Categories:** Add more categories relevant to Bangladeshi culture, such as "Family & Home" (পরিবার ও বাড়ি), "Festivals & Games" (উৎসব ও খেলা), and more specific food items under "Food & Drink" (খাবার ও পানীয়).
*   **Localized Imagery:** Replace generic emojis with custom icons or drawings that reflect Bangladeshi culture (e.g., a mango instead of an apple, a cricket bat for activities).
*   **Offline Mode:** Implement a fallback mechanism where the app can suggest common phrases from a pre-saved list if no internet connection is available.
*   **Voice Customization:** Allow the user to choose between different voices (e.g., male, female, child) to make the experience more personal.
