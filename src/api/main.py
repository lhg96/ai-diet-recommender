from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Templates setup
BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_PATH / "static")), name="static")

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
