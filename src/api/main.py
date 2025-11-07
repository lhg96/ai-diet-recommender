from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="세종시 스마트시티 식단 추천 서비스", version="0.1.0")

# Templates setup
BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_PATH / "static")), name="static")

@app.get('/')
async def read_root(request: Request):
    """메인 페이지 - 현재 구현됨"""
    return templates.TemplateResponse("index.html", {"request": request})

# TODO: 아래 API들은 미구현 상태
# @app.post('/recommend')
# async def recommend_diet():
#     """식단 추천 API - 미구현"""
#     pass
#
# @app.get('/report/{user_id}')
# async def generate_report(user_id: str):
#     """리포트 생성 API - 미구현"""
#     pass
