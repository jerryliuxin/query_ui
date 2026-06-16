#!/usr/bin/env python3
"""Debug version with exception logging"""
import json
import logging
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/mickey/.openclaw/mihua")
DD_DIR = WORKSPACE / "knowledge_base_dd"
INDEX_FILE = DD_DIR / "index.json"

try:
    index = json.loads(INDEX_FILE.read_text(encoding='utf-8'))
    logger.info(f"Index loaded: {len(index.get('companies', []))} companies")
except Exception as e:
    logger.error(f"Index load failed: {e}")
    raise

app = FastAPI(title="投研知识库", version="1.0")

try:
    templates = Jinja2Templates(directory="templates")
    logger.info("Templates loaded")
    static_dir = Path("static")
    if not static_dir.exists():
        logger.error(f"Static dir missing: {static_dir.absolute()}")
    else:
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("Static files mounted")
except Exception as e:
    logger.exception(f"Setup error: {e}")
    raise

def get_index():
    return index

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        recent = sorted(index.get("investments", []), key=lambda x: x.get("date", ""), reverse=True)[:10]
        complete_companies = []
        for comp in index.get("companies", [])[:10]:
            profile_file = DD_DIR / "companies" / comp["id"] / "profile.json"
            if profile_file.exists():
                try:
                    data = json.loads(profile_file.read_text(encoding='utf-8'))
                    if data.get("profile", {}).get("industry") and data.get("financials"):
                        complete_companies.append(comp)
                except:
                    pass
        return templates.TemplateResponse("index.html", {
            "request": request,
            "index_meta": index.get("metadata", {}),
            "recent_investments": recent,
            "complete_companies": complete_companies
        })
    except Exception as e:
        logger.exception(f"Home error: {e}")
        return HTMLResponse(f"<h1>Error: {e}</h1>", status_code=500)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8890, log_level="debug")
