CREATE TABLE emails (
    email_id TEXT PRIMARY KEY,
    sender_name VARCHAR(255),
    sender_email VARCHAR(255),
    subject VARCHAR(255),
    body TEXT[],
    snippet TEXT,
    category VARCHAR(50),
    notified BOOLEAN DEFAULT FALSE,
    responded BOOLEAN DEFAULT FALSE,
    summary TEXT
);
