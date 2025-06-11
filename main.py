from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

# Path to the HTML file
HTML_PATH = Path(__file__).parent / "static" / "index.html"

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main page with the drawing interface."""
    return HTML_PATH.read_text(encoding="utf-8")

