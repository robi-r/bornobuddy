from unittest.mock import patch
import os
import pytest
from notifier import send_notification

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "APP_EMAIL": "test_app@example.com",
        "APP_EMAIL_PASSWORD": "test_password",
        "PARENT_EMAIL": "test_parent@example.com",
    }):
        yield

def test_send_notification_success():
    """Test successful email sending."""
    with patch("notifier.smtplib.SMTP_SSL") as mock_smtp:
        mock_instance = mock_smtp.return_value
        result = send_notification("child1", "I want juice")
        assert result is True
        mock_smtp.assert_called_once_with("smtp.gmail.com", 465)
        mock_instance.login.assert_called_once_with("test_app@example.com", "test_password")
        mock_instance.send_message.assert_called_once()
        mock_instance.quit.assert_called_once()

def test_send_notification_missing_env_vars():
    """Test that notification is not sent if environment variables are missing."""
    with patch.dict(os.environ, {}, clear=True): # Clear env vars for this test
        result = send_notification("child1", "I want juice")
        assert result is False

def test_send_notification_smtp_error():
    """Test that email sending fails gracefully on SMTP error."""
    with patch("notifier.smtplib.SMTP_SSL") as mock_smtp:
        mock_smtp.side_effect = Exception("SMTP connection error")
        result = send_notification("child1", "I want juice")
        assert result is False
