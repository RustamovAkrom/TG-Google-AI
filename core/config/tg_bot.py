import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TELEGRAM_BOT_COMMANDS = [
    {"command": "/start", "description": "Start Bot"},
    {"command": "/help", "description": "Helper"},
    {"command": "/feedback", "description": "Send Feedback"},
    {"command": "/set_access_key", "description": "Set your access key from Google AI Studio"},
    {"command": "/clear_history", "description": "Clear all history"},
]

# Subscribe to my channels for using AI
REQUIRED_CHANNELS = [
    "@akrom_blog_01",
]

GETTING_GOOGLE_AI_KEY_DOCUMENTATION_URL = "https://github.com/RustamovAkrom/TG-Google-AI/blob/main/docs/getting_google_ai_key.md"
