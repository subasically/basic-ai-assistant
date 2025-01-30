import os
import time
import re
from flask import Flask, request
import schedule
from notifications import send_telegram_notification, handle_telegram_command
from chatgpt import categorize_email, summarize_email
from db_utils import save_email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)


# Telegram webhook to handle bot commands
@app.route(f"/{os.getenv('TELEGRAM_BOT_TOKEN')}", methods=["POST"])
def telegram_webhook():
    print("Received Telegram webhook.")
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        response = handle_telegram_command(text)
        send_telegram_notification({"chat_id": chat_id, "message": response})
    return {"ok": True}


# Scheduler: Fetch and process emails periodically
def scheduled_email_fetch():
    print("Running scheduled email fetch...")
    try:
        emails = fetch_new_emails()
        for email in emails:
            save_email(email)
            if (
                not email.get("notification_sent")
                and email["category"] != "notification"
            ):
                send_telegram_notification(email)
    except Exception as e:
        print("Error during scheduled email fetch:", e)


# Fetch new emails using Gmail API
def fetch_new_emails():
    print("Authenticating with Gmail API...")
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
    ]

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        print("Refreshing credentials...")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Requesting new credentials...")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    print("Fetching unread emails...")
    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q="is:unread")
        .execute()
    )
    messages = results.get("messages", [])

    print(f"Found {len(messages)} unread emails.")

    emails = []
    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        payload = msg["payload"]
        headers = payload.get("headers", [])

        # Extract key details
        sender_name = next(
            (h["value"] for h in headers if h["name"] == "From"), "Unknown"
        )
        sender_email = sender_name.split("<")[-1].split(">")[0]
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
        )
        body = parse_email_body(payload)

        # Check if the email is part of a thread
        thread_id = msg.get("threadId")
        existing_email = next(
            (email for email in emails if email["thread_id"] == thread_id), None
        )

        if existing_email:
            existing_email["body"].append(body)
        else:
            email_data = {
                "id": message["id"],
                "snippet": msg["snippet"],
                "sender_name": sender_name,
                "sender_email": sender_email,
                "subject": subject,
                "body": [body],
                "category": (
                    categorize_email({"subject": subject, "body": body})
                    if subject or body
                    else "other"
                ),
                "notification_sent": False,
                "summary": (
                    summarize_email({"subject": subject, "body": body})
                    if subject or body
                    else ""
                ),
                "thread_id": thread_id,
            }
            emails.append(email_data)
    return emails


# Parse email body
def parse_email_body(payload):
    """Extracts the plain text body from an email payload."""
    try:
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body_data = part["body"].get("data", "")
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                        return re.sub(r"\n+", "\n", body).strip()  # Clean up newlines
        else:
            body_data = payload["body"].get("data", "")
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                return re.sub(r"\n+", "\n", body).strip()

    except Exception as e:
        print("Error parsing email body:", e)

    return ""


# Schedule the email fetch
schedule.every(int(os.getenv("SCHEDULE", 5))).minutes.do(scheduled_email_fetch)

# Main entry point
if __name__ == "__main__":
    from threading import Thread

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    Thread(target=run_scheduler).start()
    app.run(host="0.0.0.0", port=5000)
