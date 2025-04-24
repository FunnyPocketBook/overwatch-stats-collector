from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SAVE_DIR = "match_data"
os.makedirs(SAVE_DIR, exist_ok=True)

SECRET = os.getenv("SECRET")


@app.post("/match")
async def receive_match(request: Request, x_secret: str = Header(None)):
    if x_secret != SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret phrase")

    data = await request.json()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    filename = os.path.join(SAVE_DIR, f"match-{timestamp}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return {"status": "saved", "file": filename}
