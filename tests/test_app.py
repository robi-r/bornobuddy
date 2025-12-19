from unittest.mock import Mock, patch
import pytest
import json
from app import (
    get_current_datetime,
    build_context,
    parse_model_output,
    load_prompt_template,
)

# Mock streamlit session state
@pytest.fixture(autouse=True)
def mock_session_state():
    with patch("app.st.session_state", new_callable=Mock) as mock_state:
        mock_state.latitude = None
        mock_state.longitude = None
        mock_state.location_name = None
        
        # Configure the mock's get method
        def get_side_effect(key, default=None):
            if key == "last_phrase":
                return "Hello"
            return default
        
        mock_state.get.side_effect = get_side_effect
        yield mock_state

def test_get_current_datetime():
    """Test that get_current_datetime returns the correct keys."""
    dt = get_current_datetime()
    assert "date" in dt
    assert "time" in dt
    assert "day_of_week" in dt
    assert "time_of_day" in dt

def test_build_context(mock_session_state):
    """Test that build_context builds the context dictionary correctly."""
    mock_session_state.latitude = 12.34
    mock_session_state.longitude = 56.78
    mock_session_state.location_name = "Test Location"

    context = build_context("Test Category")
    assert context["child_id"] == "demo_child"
    assert context["category"] == "Test Category"
    assert "12.34" in context["location"]
    assert "56.78" in context["location"]
    assert "Test Location" in context["location"]
    assert context["last_phrase"] == "Hello"

def test_parse_model_output_format1():
    """Test parsing the first valid model output format (dict with phrases)."""
    raw_text = """
    ```json
    {
      "phrases": [
        {"text": "Hello", "emoji": "👋"},
        {"text": "How are you?", "emoji": "😊"},
        {"text": "Goodbye", "emoji": "✅"}
      ]
    }
    ```
    """
    phrases = parse_model_output(raw_text)
    assert len(phrases) == 3
    assert phrases[0] == {"text": "Hello", "emoji": "👋"}

def test_parse_model_output_format2():
    """Test parsing the second valid model output format (list of lists)."""
    raw_text = """
    ```json
    [
      ["Hello", "👋"],
      ["How are you?", "😊"],
      ["Goodbye", "✅"]
    ]
    ```
    """
    phrases = parse_model_output(raw_text)
    assert len(phrases) == 3
    assert phrases[1] == {"text": "How are you?", "emoji": "😊"}

def test_parse_model_output_invalid_json():
    """Test that parsing invalid JSON raises an error."""
    with pytest.raises(json.JSONDecodeError):
        parse_model_output("not json")

def test_parse_model_output_wrong_length():
    """Test that parsing a list with the wrong number of phrases raises an error."""
    with pytest.raises(ValueError):
        parse_model_output('[["Hello", "👋"]]')

def test_parse_model_output_missing_fields():
    """Test that parsing with missing fields raises an error."""
    with pytest.raises(ValueError):
        parse_model_output('[{"text": "Hello"}]') # Missing emoji

def test_load_prompt_template():
    """Test that the correct prompt template is loaded."""
    # This test assumes the prompt files exist
    prompt_en = load_prompt_template("en")
    assert "Generate all phrases in **English**" in prompt_en

    prompt_bn = load_prompt_template("bn")
    assert "Generate all phrases in **Bengali (Bangla)**" in prompt_bn

    # Test fallback
    prompt_fallback = load_prompt_template("xx") # non-existent language
    assert "Generate three short, simple phrases" in prompt_fallback
