import os
import openai

# Get categories from .env
EMAIL_CATEGORIES = os.getenv(
    "EMAIL_CATEGORIES", "spam,personal,bill,invite,school,notification"
).split(",")

MY_NAME = os.getenv("MY_NAME", "John Doe")

client = openai.OpenAI(
    api_key=os.getenv(
        "OPENAI_API_KEY",
        "",
    )
)


# Categorize email using ChatGPT
def categorize_email(email_data):
    try:
        print(f"Categorizing {email_data['subject']} email...")
        categories_str = ", ".join(EMAIL_CATEGORIES)

        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an AI assistant designed to categorize emails into one of the following categories: {categories_str}. "
                        "When provided with an email subject and body, analyze the content and assign it to the most appropriate category. "
                        "Use the context and tone of the email to make an accurate determination. Respond with only the category name."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Here is the email:\n"
                        f"Subject: \"{email_data['subject']}\"\n"
                        f"Body: \"{email_data['body']}\"\n\n"
                        "Based on the provided information, what category does this email belong to? Respond with only the category name."
                    ),
                },
            ],
        )

        category = completion.choices[0].message.content.strip("'").lower()

        if category in EMAIL_CATEGORIES:
            print(f"Email categorized as: {category}")
            return category
        else:
            print(f"Email categorized as: other")
            return "other"
    except Exception as e:
        print("Error categorizing email:", e)
        return "error"


def summarize_email(email_data):
    try:
        print(f"Summarizing {email_data['subject']} email...")
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant designed to summarize emails. "
                        "When provided with an email subject and body, generate a concise summary of the email content. "
                        f"Use the context and key points to create an informative summary. Respond with the summary text as a paragraph. My name is {MY_NAME}."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Here is the email:\n"
                        f"Subject: \"{email_data['subject']}\"\n"
                        f"Body: \"{email_data['body']}\"\n\n"
                        "Can you provide a summary of this email?"
                    ),
                },
            ],
        )

        summary = completion.choices[0].message.content.strip("'")
        print(f"Email summary: {summary}")
        return summary
    except Exception as e:
        print("Error summarizing email:", e)
        return "Error summarizing email"


# if __name__ == "__main__":
#     # Set environment variables for testing
#     os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

#     # Test data
#     email_data = {
#         "subject": "Meeting Reminder",
#         "body": "Don't forget about the meeting tomorrow at 10 AM.",
#     }

#     # Call the function and print the result
#     category = categorize_email(email_data)
#     print(f"Category: {category}")
