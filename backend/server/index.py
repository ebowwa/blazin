# app/index.py


# **WARNING: DO NOT OMIT ANYTHING FROM THE FOLLOWING**,
# if changing add notes be concise to what was done and why


# TODO: 
# - rules for using the numbers: 
# 1. only use one number twice per day max to avoid flag
# 2. rename generic `review_gemini_extracted_image_phone_numbers.json` to `review_{ip_address}_gemini_extracted_image_phone_numbers.json`
# 3. to share numbers with the community

from fastapi import FastAPI
from logging_setup import setup_logging
from route.features.collect_phone_numbers import router as phone_numbers_router
from route.features.extract_phone_numbers import router as gemini_flash8b_router
from route.templates.index import router as template_routes
import uvicorn

# Initialize logging
setup_logging()
# Initialize FastAPI app
app = FastAPI()
# Include routers
app.include_router(phone_numbers_router, prefix="/phone_numbers", tags=["Phone Numbers"])
app.include_router(gemini_flash8b_router, prefix="/gemini_flash8b", tags=["Gemini Flash-8B"])
app.include_router(template_routes)

# ------------------------------------------------------
# Run the FastAPI app using Uvicorn
# ------------------------------------------------------

if __name__ == "__main__":
    # Increase the request size limit if necessary (e.g., 10 MB)
    uvicorn.run("index:app", host="0.0.0.0", port=8000, reload=True)  # 10 MB
