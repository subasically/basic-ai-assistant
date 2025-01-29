# Basic AI Assistant

This project is a basic AI assistant that categorizes emails using OpenAI's GPT-3 and sends notifications via Telegram. It uses the Gmail API to fetch unread emails, categorizes them, and stores them in a PostgreSQL database.

## Features

- Fetches unread emails from Gmail.
- Categorizes emails into 'spam', 'personal', or 'notification' using GPT-3.
- Stores categorized emails in a PostgreSQL database.
- Sends notifications for personal and notification emails via Telegram.

## Prerequisites

- Docker and Docker Compose
- Python 3.10
- Google Cloud project with Gmail API enabled
- OpenAI API key
- Telegram bot token and chat ID

## Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/basic-ai-assistant.git
   cd basic-ai-assistant
   ```

2. Create a `credentials.json` file with your Google Cloud credentials:

   ```json
   {
     "web": {
       "client_id": "YOUR_CLIENT_ID",
       "project_id": "YOUR_PROJECT_ID",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_secret": "YOUR_CLIENT_SECRET",
       "redirect_uris": ["http://localhost", "http://localhost:8080/"]
     }
   }
   ```

3. Create a `token.json` file with your OAuth2 token:

   ```json
   {
     "token": "YOUR_TOKEN",
     "refresh_token": "YOUR_REFRESH_TOKEN",
     "token_uri": "https://oauth2.googleapis.com/token",
     "client_id": "YOUR_CLIENT_ID",
     "client_secret": "YOUR_CLIENT_SECRET",
     "scopes": ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"],
     "universe_domain": "googleapis.com",
     "account": "",
     "expiry": "YOUR_EXPIRY_DATE"
   }
   ```

4. Create a `.env` file with your environment variables:

   ```env
   TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID
   TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   OPENAI_API_KEY=YOUR_OPENAI_API_KEY
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=password
   POSTGRES_DB=email_db
   POSTGRES_HOST=postgres
   ```

5. Build and run the Docker containers:
   ```sh
   docker-compose up --build
   ```

## Usage

The application will fetch unread emails every 5 minutes, categorize them, store them in the database, and send notifications for personal and notification emails.

## Files

- `app.py`: Main application script.
- `notifications.py`: Script for sending notifications via Telegram.
- `db_init.sql`: SQL script for initializing the database.
- `Dockerfile`: Dockerfile for building the application image.
- `docker-compose.yml`: Docker Compose configuration.
- `requirements.txt`: Python dependencies.

## License

This project is licensed under the MIT License.
