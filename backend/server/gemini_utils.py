# utils.py

import re
import os
import json
import logging
from typing import Optional
from uuid import uuid4
import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_FLASH8B_GENERATION_CONFIG 

# Configure logging settings
logger = logging.getLogger(__name__)

# ------------------------------------------------------
# Initialize Google Gemini configuration
# ------------------------------------------------------
genai.configure(api_key=GOOGLE_API_KEY)

gemini_flash8b_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-8b",
    generation_config=GEMINI_FLASH8B_GENERATION_CONFIG,  # Correct variable name
)

# ------------------------------------------------------
# Utility Functions
# ------------------------------------------------------

def gemini_flash8b_upload_file(path: str, mime_type: Optional[str] = None):
    """Uploads the given file to Gemini Flash-8B.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    logger.info(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def gemini_flash8b_validate_phone_number(phone_number: str) -> str:
    """Validates and formats a phone number."""
    clean_number = re.sub(r'\D', '', phone_number)
    if len(clean_number) == 11 and clean_number.startswith("1"):
        clean_number = clean_number[1:]
    if len(clean_number) != 10:
        raise ValueError("Invalid USA phone number. Please enter a valid 10-digit number.")
    formatted_number = f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}"
    return formatted_number
