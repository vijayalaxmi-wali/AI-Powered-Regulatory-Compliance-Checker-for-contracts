from dotenv import load_dotenv
import os

load_dotenv()

import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests

# ==============================
# CONFIGURATION (from .env)
# ==============================
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")   # Gmail App Password
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Slack Webhook URL 
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# ==============================
# EMAIL NOTIFICATION FUNCTION
# ==============================
def send_email_notification(subject, message):
    """
    Sends an email notification via Gmail SMTP with robust error handling.
    """
    try:
        # Add timestamp for context
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Email message
        full_message = f"Timestamp: {current_time}\n\n{message}"
        msg = MIMEText(full_message)
        msg["Subject"] = subject
        msg["From"] = f"Vijayalaxmi <{SENDER_EMAIL}>"
        msg["To"] = RECEIVER_EMAIL

        # Connect to Gmail server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"[Email] ✅ Sent successfully → {subject}")

    except Exception as e:
        print("[Email] ❌ Error occurred:", e)

# ==============================
# SLACK NOTIFICATION FUNCTION
# ==============================
def send_slack_notification(message):
    """
    Sends a real-time alert message to Slack channel using Incoming Webhook.
    """
    try:
        payload = {
            "text": message,
            "username": "ComplianceBot 🕵️‍♂️",
            "icon_emoji": ":shield:"
        }
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)

        if response.status_code == 200:
            print("[Slack] ✅ Notification sent successfully!")
        else:
            print(f"[Slack] ❌ Failed to send message. Status Code: {response.status_code}")

    except Exception as e:
        print("[Slack] ❌ Error occurred while sending Slack notification:", e)

# ==============================
# COMBINED FUNCTION
# ==============================
def send_notification(subject, message, include_slack=True):
    """
    Sends both email and Slack notifications.
    Parameters:
        subject (str): Email subject line
        message (str): Email/Slack message body
        include_slack (bool): Whether to also send Slack notification (default: True)
    """
    send_email_notification(subject, message)

    if include_slack:
        slack_msg = f"*{subject}*\n{message}"
        send_slack_notification(slack_msg)

# ==============================
# SAMPLE TEST (Uncomment to Test)
# ==============================
if __name__ == "__main__":
    # Example 1: Error notification
    try:
        x = 1 / 0
    except Exception as e:
        send_notification(
            subject="⚠️ Error occurred in Data Extraction Phase",
            message=f"Function: Clause_extraction()\nError: {e}"
        )

    # Example 2: Comparison result
    send_notification(
        subject="📊 Comparison Result",
        message="Agreement type: DPA\nComparison Result: All clauses matched successfully."
    )
