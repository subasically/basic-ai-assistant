import psycopg2
from psycopg2.extras import DictCursor
import os


def connect_to_db():
    print("Connecting to the database...")
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", 5432),
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None


def save_email(email_data):
    print("Saving email to database...")
    conn = connect_to_db()
    if conn is None:
        return

    cursor = conn.cursor()
    query = """
    INSERT INTO emails (email_id, sender_name, sender_email, subject, body, snippet, category, notified)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (email_id)
    DO UPDATE SET
        sender_name = EXCLUDED.sender_name,
        sender_email = EXCLUDED.sender_email,
        subject = EXCLUDED.subject,
        body = EXCLUDED.body,
        snippet = EXCLUDED.snippet,
        category = EXCLUDED.category;
    """
    cursor.execute(
        query,
        (
            email_data["id"],
            email_data["sender_name"],
            email_data["sender_email"],
            email_data["subject"],
            email_data["body"],
            email_data["snippet"],
            email_data["category"],
            email_data.get("notified", False),
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def fetch_unnotified_emails():
    print("Fetching unnotified emails...")
    conn = connect_to_db()
    if not conn:
        return []

    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT * FROM emails WHERE notified = FALSE")
    emails = cursor.fetchall()
    cursor.close()
    conn.close()
    return emails


def mark_as_notified(email_id):
    conn = connect_to_db()
    if not conn:
        return

    cursor = conn.cursor()
    cursor.execute("UPDATE emails SET notified = TRUE WHERE email_id = %s", (email_id,))
    conn.commit()
    cursor.close()
    conn.close()
