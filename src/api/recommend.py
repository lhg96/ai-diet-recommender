"""
식단 추천 엔진 — nutriwise-diet-recommender 의 동작 로직을 FastAPI 구조로 이식한 모듈.

이식 원본: nutriwise-diet-recommender/main.py
- 목적별 필터 (Weight_Loss / Muscle_Gain / Weight_Gain)
- 영양 필터 (채식·철분>6mg·칼슘>150mg)
- 추천 식품 카드 생성 (build_food_cards)
- 식품 검색/정렬 (read_rows_for_search)

데이터 소스: USDA done_food_data.csv → 한국 식약처 기반 korean_food_data.csv 로 전환
(컬럼명은 nutriwise 와 호환: Descrip, category, Energy_kcal, Protein_g, ...)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
KOREAN_DATA_PATH = BASE_DIR / "data" / "korean_food_data.csv"
USDA_DATA_PATH = BASE_DIR / "data" / "done_food_data.csv"

# 채식 필터에서 제외할 육류/어패류 키워드 (nutriwise 원본 유지)
EXCLUDE_KEYWORDS = [
    "egg", "fish", "meat", "beef", "chicken", "deer", "lamb", "crab", "pork",
    "turkey", "flesh", "shrimp", "octopus", "ostrich", "emu", "crayfish",
    "cuttlefish",
]

# 한글 채식 제외 키워드 (한국 데이터 전환 시 추가)
KOREAN_EXCLUDE_KEYWORDS = [
    "닭", "소고기", "돼지", "삼겹살", "갈비", "보쌈", "치킨", "참치",
    "연어", "멸치", "새우", "탕수육", "오리", "계란", "어묵", "육개장",
    "감자탕", "돼지국밥", "장어", "고등어", "꽁치", "조기", "갈치",
    "오징어", "갑오징어", "조개", "해물", "굴", "멍게", "전복", "문어",
]

DIET_LABELS = {
    "musclegain": "Muscle_Gain",
    "weightgain": "Weight_Gain",
    "weightloss": "Weight_Loss",
}

# 카테고리별 표시명 (한국어)
DIET_LABELS_KO = {
    "musclegain": "근육 증가",
    "weightgain": "체중 증량",
    "weightloss": "체중 감량",
}

REQUIRED_COLUMNS = {
    "Descrip", "category", "Energy_kcal", "Protein_g", "Fat_g", "Sugar_g",
    "Iron_mg", "Calcium_mg", "Fiber_g",
}


@dataclass
class DietFilters:
    """영양 필터 — nutriwise DietFilters 이식"""

    vegetarian: bool = False
    iron: bool = False
    calcium: bool = False
    anyfoods: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "DietFilters":
        def has(option: str) -> bool:
            value = data.get(option)
            if isinstance(value, str):
                return value.lower() in ("1", "true", "on", "yes", option)
            return bool(value)

        return cls(
            vegetarian=has("vegetarian"),
            iron=has("iron"),
            calcium=has("calcium"),
            anyfoods=has("anyfoods"),
        )

    @classmethod
    def from_form(cls, form) -> "DietFilters":
        """Jinja2/FormData 호환 (list 값 처리)"""

        def has(option: str) -> bool:
            if form is None:
                return False
            if hasattr(form, "getlist"):
                values = form.getlist(option)
            else:
                values = [form.get(option)] if form.get(option) else []
            return any(v.lower() in ("1", "true", "on", "yes", option) for v in values) if values else bool(form.get(option))

        return cls(
            vegetarian=has("vegetarian"),
            iron=has("iron"),
            calcium=has("calcium"),
            anyfoods=has("anyfoods"),
        )

    def any_selected(self) -> bool:
        return self.vegetarian or self.iron or self.calcium or self.anyfoods


def _load_food_data() -> pd.DataFrame:
    """한국 데이터 우선, 없으면 USDA 폴백. 컬럼 누락 시 빈 DataFrame 반환."""
    for path in (KOREAN_DATA_PATH, USDA_DATA_PATH):
        if path.exists():
            try:
                df = pd.read_csv(path, encoding="utf-8-sig")
            except Exception:
                df = pd.read_csv(path, encoding="utf-8")
            missing_cols = REQUIRED_COLUMNS - set(df.columns)
            if not missing_cols:
                return df
    return pd.DataFrame(columns=sorted(REQUIRED_COLUMNS))


FOOD_DATA: pd.DataFrame = _load_food_data()


def build_food_cards(data: pd.DataFrame, limit: int = 5) -> List[Dict[str, str]]:
    """추천 식품 카드 생성 — nutriwise build_food_cards 이식"""
    if data.empty or limit <= 0:
        return []
    sample = data.sample(n=min(limit, len(data)), replace=False, random_state=None)
    cards = []
    for _, row in sample.iterrows():
        cards.append(
            {
                "name": str(row.get("Descrip", "Unknown food")),
                "calories": f"{row.get('Energy_kcal', 0):.0f} kcal",
                "protein": f"{row.get('Protein_g', 0):.1f} g",
                "iron": f"{row.get('Iron_mg', 0):.1f} mg",
                "calcium": f"{row.get('Calcium_mg', 0):.0f} mg",
                "fiber": f"{row.get('Fiber_g', 0):.1f} g",
            }
        )
    return cards


def apply_diet_filters(category: str, filters: DietFilters) -> pd.DataFrame:
    """목적별 카테고리 + 영양 필터 적용 — nutriwise apply_diet_filters 이식"""
    if FOOD_DATA.empty:
        return FOOD_DATA

    filtered = FOOD_DATA[FOOD_DATA["category"] == DIET_LABELS[category]].copy()
    base = filtered.copy()

    if filters.iron:
        filtered = filtered[filtered["Iron_mg"] > 6]

    if filters.calcium:
        filtered = filtered[filtered["Calcium_mg"] > 150]

    if filters.vegetarian:
        pattern = "|".join(EXCLUDE_KEYWORDS + KOREAN_EXCLUDE_KEYWORDS)
        filtered = filtered[
            ~filtered["Descrip"].str.contains(pattern, case=False, na=False)
        ]

    if filters.anyfoods or not filters.any_selected():
        filtered = base

    return filtered


def read_rows_for_search(sort_by: str, query: str) -> Sequence[Dict[str, str]]:
    """식품 검색/정렬 — nutriwise read_rows_for_search 이식"""
    if FOOD_DATA.empty:
        return []

    sort_column = sort_by if sort_by in FOOD_DATA.columns else "Descrip"
    rows = FOOD_DATA.sort_values(by=sort_column).copy()
    if query:
        rows = rows[rows["Descrip"].str.contains(query, case=False, na=False)]
    return rows.to_dict(orient="records")


SEARCH_COLUMNS = [
    ("Descrip", "음식명"),
    ("category", "목적 카테고리"),
    ("Energy_kcal", "칼로리(kcal)"),
    ("Fat_g", "지방(g)"),
    ("Protein_g", "단백질(g)"),
    ("Sugar_g", "당류(g)"),
    ("Iron_mg", "철분(mg)"),
    ("Calcium_mg", "칼슘(mg)"),
    ("Fiber_g", "식이섬유(g)"),
]
