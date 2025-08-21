import os


# 🔑 API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ⚙️ Основные параметры генерации
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", 1024))
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", 0.7))
GEMINI_TOP_K = int(os.getenv("GEMINI_TOP_K", 40))
GEMINI_TOP_P = float(os.getenv("GEMINI_TOP_P", 0.95))
GEMINI_SEED = int(os.getenv("GEMINI_SEED", 42))  # можно оставить None

# History memories conf
GEMINI_MAX_HISTORY_CHARS = 3000
GEMINI_MAX_HISTORY_LIMIT = 3
