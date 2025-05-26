from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import csv
import json
from datetime import datetime
import sys


sys.path.append(str(Path(__file__).resolve().parent.parent))


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

TOURS_FILE = Path("data/tours.csv")
HOTELS_FILE = Path("data/hotels.csv")
BROADCAST_FILE = Path("data/broadcast.txt")
STATUS_FILE = Path("data/status.json")

def load_status():
    if STATUS_FILE.exists():
        with open(STATUS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"tours": {}, "hotels": {}}

def save_status(data):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    only_new = request.query_params.get('only_new') == 'on'

    tours, hotels = [], []
    status = load_status()

    if TOURS_FILE.exists():
        with open(TOURS_FILE, encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                next(reader)
            except StopIteration:
                reader = []
            for row in reader:
                key = row[0] + row[2]
                handled = status.get("tours", {}).get(key, False)
                date_str = row[0].split()[0]
                if from_date and date_str < from_date:
                    continue
                if to_date and date_str > to_date:
                    continue
                if only_new and handled:
                    continue
                tours.append((row, handled))

    if HOTELS_FILE.exists():
        with open(HOTELS_FILE, encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                next(reader)
            except StopIteration:
                reader = []
            for row in reader:
                key = row[0] + row[2]
                handled = status.get("hotels", {}).get(key, False)
                date_str = row[0].split()[0]
                if from_date and date_str < from_date:
                    continue
                if to_date and date_str > to_date:
                    continue
                if only_new and handled:
                    continue
                hotels.append((row, handled))

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tours": tours,
        "hotels": hotels,
        "from_date": from_date,
        "to_date": to_date,
        "only_new": only_new
    })

@app.post("/broadcast")
async def save_broadcast(
    title: str = Form(...),
    message: str = Form(...),
    image_url: str = Form(None)
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    broadcast_text = f"{now}\n{title}\n{message}\n{image_url or ''}"
    BROADCAST_FILE.write_text(broadcast_text, encoding="utf-8")
    return RedirectResponse("/", status_code=302)

@app.post("/mark_handled")
async def mark_handled(type: str = Form(...), key: str = Form(...)):
    status = load_status()
    status[type][key] = True
    save_status(status)
    return JSONResponse({"ok": True})

@app.post("/send_broadcast_now")
async def send_broadcast_now():
    from broadcast import send_broadcast
    await send_broadcast()
    return JSONResponse({"ok": True})
