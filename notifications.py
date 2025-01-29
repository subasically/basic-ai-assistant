import requests
import os
import psycopg2
from psycopg2.extras import DictCursor


# Mark as notified in the database
def mark_as_notified(email_id):
    try:
        conn = psycopg2.connect(
            dbname="email_db",
            user="admin",
            password="password",
            host="postgres",
            port=5432,
        )
        cursor = conn.cursor()
        query = "UPDATE emails SET notified = TRUE WHERE email_id = %s"
        cursor.execute(query, (email_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Email {email_id} marked as notified.")
    except Exception as e:
        print("Error marking email as notified:", e)


# Send notification via Telegram
def send_telegram_notification(email_data):
    print("Sending Telegram notification...")
    # print(email_data)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    message = (
        f"<b>From:</b> {email_data['sender_name'].capitalize()}\n"
        f"<b>Subject:</b> {email_data['subject'].capitalize()}\n"
        f"<b>Category:</b> {email_data['category'].capitalize()}\n"
        f"<b>Summary:</b> {email_data['summary']}"
    )
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Notification sent successfully.")
            mark_as_notified(email_data["id"])  # Mark as notified
        else:
            print("Failed to send notification:", response.text)
    except Exception as e:
        print("Error sending Telegram notification:", e)


# Handle telegram commands
def handle_telegram_command():
    try:
        conn = psycopg2.connect(
            dbname="email_db",
            user="admin",
            password="password",
            host="postgres",  # Use the service name defined in docker-compose
            port=5432,
        )
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(
            "SELECT email_id, sender_name, sender_email, subject, category FROM emails"
        )
        emails = cursor.fetchall()
        cursor.close()
        conn.close()

        if not emails:
            return "No emails found."

        response = "Here are your stored emails:\n"
        for email in emails:
            response += (
                f"ID: {email['email_id']}, Sender: {email['sender_email']}, "
                f"Subject: {email['subject']}, Category: {email['category']}\n"
            )
        return response

    except Exception as e:
        print("Error fetching emails:", e)
        return "An error occurred while fetching emails."


# send_telegram_notification(
#     {"sender_name": "john", "subject": "hello", "category": "important", "id": 1}
# )
