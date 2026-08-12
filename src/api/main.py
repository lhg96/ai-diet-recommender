"""
AI Diet Recommender — 통합본 FastAPI 서버

① ai-diet-recommender (FastAPI + 식약처 한국 데이터 + BMR 모델) 본체
② nutriwise-diet-recommender (목적별 필터/카드/검색 추천 로직) 흡수

라우트:
    GET  /                     메인 페이지
    GET  /recommend            추천 페이지 (BMR 입력 + 목적별 필터 폼)
    POST /recommend            목적별 추천 (form: goal, vegetarian, iron, calcium, limit)
    POST /api/calculate-bmr    BMR → 권장 칼로리 (JSON)
    POST /predict              식단 유형 분류 예측 (JSON: calories, protein, fiber)
    GET  /search               식품 검색/정렬 (?q=&sort=)
"""
from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.api import recommend
from src.api.models import bmr as bmr_model
from src.api.models import classifier as classifier_model

app = FastAPI(title="AI Diet Recommender — 개인 맞춤 식단 추천", version="1.0.0")

BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

# Static files
app.mount("/static", StaticFiles(directory=str(BASE_PATH / "static")), name="static")

# 라우트 이름 → 템플릿 렌더 헬퍼 (Starlette 1.x 호환 시그니처)
def render(request: Request, name: str, **context):
    return templates.TemplateResponse(request, name, context)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """메인 페이지"""
    return render(
        request,
        "index.html",
        food_count=len(recommend.FOOD_DATA),
        bmr_ready=bmr_model.load_model(),
    )


@app.get("/recommend", response_class=HTMLResponse)
async def recommend_page(request: Request):
    """추천 페이지 (BMR 입력 + 목적별 필터)"""
    return render(
        request,
        "recommend.html",
        result=None,
        error=None,
        success=False,
        inputs={},
        musclegainfoods=[],
        weightgainfoods=[],
        weightlossfoods=[],
    )


@app.post("/recommend", response_class=HTMLResponse)
async def recommend_diet(
    request: Request,
    goal: str = Form("weightloss"),
    vegetarian: Optional[str] = Form(None),
    iron: Optional[str] = Form(None),
    calcium: Optional[str] = Form(None),
    anyfoods: Optional[str] = Form(None),
    limit: int = Form(5),
):
    """목적별 추천 — nutriwise handle_diet_view 이식 (데이터: 한국 식약처 기반)"""
    if recommend.FOOD_DATA.empty:
        return render(request, "recommend.html", error="식품 데이터를 불러올 수 없습니다. `data/korean_food_data.csv` 파일을 확인하세요.", inputs={})

    if goal not in recommend.DIET_LABELS:
        return render(request, "recommend.html", error=f"올바르지 않은 목적입니다: {goal}", inputs={})

    filters = recommend.DietFilters(
        vegetarian=bool(vegetarian),
        iron=bool(iron),
        calcium=bool(calcium),
        anyfoods=bool(anyfoods),
    )
    filtered_data = recommend.apply_diet_filters(goal, filters)

    context_key = f"{goal}foods"
    cards = recommend.build_food_cards(filtered_data, limit=min(limit, 20))
    if not cards:
        return render(
            request,
            "recommend.html",
            error="조건에 맞는 식품을 찾지 못했습니다. 필터를 조정해주세요.",
            inputs={"goal": goal},
        )
    return render(
        request,
        "recommend.html",
        success=True,
        error=None,
        inputs={"goal": goal},
        result=f"{recommend.DIET_LABELS_KO[goal]} 목표 추천 {len(cards)}개 식품",
        **{context_key: cards},
    )


@app.post("/api/calculate-bmr")
async def calculate_bmr(
    age: float = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    gender: str = Form("Male"),
    activity: str = Form("light"),
    goal: str = Form("weightloss"),
):
    """BMR 예측 + 권장 칼로리 계산 (기획서 API 명세: POST /api/calculate-bmr)"""
    if not (age > 0 and weight > 0 and height > 0):
        return JSONResponse({"error": "나이·체중·키는 0보다 커야 합니다."}, status_code=400)

    bmr_value = bmr_model.predict_bmr(age, weight, height, gender)
    if bmr_value is None:
        return JSONResponse(
            {"error": "BMR 모델을 찾을 수 없습니다. `python mlops/train_bmr.py` 로 재학습하세요."},
            status_code=503,
        )

    result = bmr_model.calculate_daily_calories(bmr_value, activity=activity, goal=goal)
    return JSONResponse(result)


@app.post("/predict")
async def predict(
    calories: float = Form(...),
    protein: float = Form(...),
    fiber: float = Form(...),
):
    """식단 유형 분류 예측 — nutriwise /predict 이식"""
    if any(v < 0 for v in (calories, protein, fiber)):
        return JSONResponse({"error": "모든 입력값은 0 이상이어야 합니다."}, status_code=400)

    prediction = classifier_model.predict_diet_type(calories, protein, fiber)
    if prediction is None:
        return JSONResponse(
            {"error": "분류 모델을 찾을 수 없습니다. `python mlops/train_classifier.py` 로 재학습하세요."},
            status_code=503,
        )
    return JSONResponse({"prediction": prediction})


@app.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    q: str = Query(""),
    sort: str = Query("Descrip"),
):
    """식품 검색/정렬 — nutriwise search 이식 (한글화)"""
    rows = recommend.read_rows_for_search(sort, q.strip())
    return render(
        request,
        "search.html",
        rows=rows,
        query=q.strip(),
        sort_by=sort,
        columns=recommend.SEARCH_COLUMNS,
    )
