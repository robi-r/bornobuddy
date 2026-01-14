import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

APP_EMAIL = os.getenv("APP_EMAIL")
APP_EMAIL_PASSWORD = os.getenv("APP_EMAIL_PASSWORD")
PARENT_EMAIL = os.getenv("PARENT_EMAIL")

def send_notification(child_id: str, phrase: str) -> bool:
    """
    Sends an email notification to the parent's email address when a child selects a phrase.
    """
    if not APP_EMAIL or not APP_EMAIL_PASSWORD or not PARENT_EMAIL:
        print("Notification not sent: Email configuration (APP_EMAIL, APP_EMAIL_PASSWORD, PARENT_EMAIL) is incomplete in .env")
        return False

    sender_email = APP_EMAIL
    receiver_email = PARENT_EMAIL
    password = APP_EMAIL_PASSWORD

    message = MIMEText(f"Child {child_id} selected the phrase: '{phrase}'.")
    message["Subject"] = f"BornoBuddy: Child {child_id} Communication Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(message)
        print(f"Notification sent to {receiver_email}: Child {child_id} selected '{phrase}'")
        return True
    except Exception as e:
        print(f"Error sending notification email: {e}")
        return False

if __name__ == "__main__":
    # Example usage for testing
    print("Attempting to send a test notification...")
    test_child_id = "test_child_123"
    test_phrase = "I want to eat."
    if send_notification(test_child_id, test_phrase):
        print("Test notification successful (check parent's email).")
    else:
        print("Test notification failed. Check .env settings and network connection.")
