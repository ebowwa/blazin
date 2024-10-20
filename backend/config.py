# config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load the environment variables

# Google Gemini configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Gemini Flash-8B generation configuration
GEMINI_FLASH8B_GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Filepaths for the JSON storage files
PHONE_NUMBERS_JSON_FILE = "phone_numbers_db.json"
GEMINI_TEMP_JSON_FILE = "gemini_flash8b_temp_db.json"
