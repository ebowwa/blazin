# route/templates/index.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

@router.get("/test", response_class=HTMLResponse)
async def serve_html():
    file_path = os.path.join(os.path.dirname(__file__), "test.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Test HTML file not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, media_type="text/html")
