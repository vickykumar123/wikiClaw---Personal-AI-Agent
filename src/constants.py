# ============================================
# CONSTANTS - Single source of truth
# ============================================

# === Context Types ===
CONTEXT_TYPE_PROFILE = "profile"
CONTEXT_TYPE_PREFERENCE = "preference"
CONTEXT_TYPE_FACT = "fact"
CONTEXT_TYPE_TOPIC = "topic"
CONTEXT_TYPE_EVENT = "event"
CONTEXT_TYPE_SESSION = "session"

# === Context Limits (max entries per type) ===
MAX_PROFILE_ENTRIES = 5
MAX_PREFERENCE_ENTRIES = 10
MAX_FACT_ENTRIES = 20
MAX_TOPIC_ENTRIES = 10
MAX_EVENT_ENTRIES = 10
MAX_SESSION_ENTRIES = 10

# Mapping: type -> limit
CONTEXT_LIMITS = {
    CONTEXT_TYPE_PROFILE: MAX_PROFILE_ENTRIES,
    CONTEXT_TYPE_PREFERENCE: MAX_PREFERENCE_ENTRIES,
    CONTEXT_TYPE_FACT: MAX_FACT_ENTRIES,
    CONTEXT_TYPE_TOPIC: MAX_TOPIC_ENTRIES,
    CONTEXT_TYPE_EVENT: MAX_EVENT_ENTRIES,
    CONTEXT_TYPE_SESSION: MAX_SESSION_ENTRIES,
}

# === Conversation Context ===
MAX_RECENT_MESSAGES = 15
MAX_CONTEXT_TOKENS = 4000

# === Webhook Defaults ===
DEFAULT_WEBHOOK_PORT = 8443
DEFAULT_WEBHOOK_PATH = "/webhook"

# === Ollama Defaults ===
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "gpt-oss:120b-cloud"

# === File Paths ===
SUMMARIES_DIR = "data/summaries"
SUMMARY_FILE_PREFIX = "user_"
SUMMARY_FILE_EXTENSION = ".jsonl"

# === Google Calendar ===
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]

# === Error Messages ===
ERROR_MISSING_TELEGRAM_TOKEN = "TELEGRAM_BOT_TOKEN is required in .env"
ERROR_MISSING_OPENAI_KEY = "OPENAI_API_KEY is required in .env"
ERROR_MISSING_MONGODB_URI = "MONGODB_URI is required in .env"
ERROR_OLLAMA_CONNECTION = "Failed to connect to Ollama"
ERROR_WEBHOOK_SETUP = "Failed to set up webhook"

# === Success Messages ===
MSG_BOT_STARTED = "Bot started successfully"
MSG_WEBHOOK_SET = "Webhook set successfully"

# === Logging ===
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
