"""
식단 카테고리 분류 모델 모듈 — nutriwise /predict 로직 이식.

모델 파일: models/food_model.pickle
재학습:     python mlops/train_classifier.py
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Optional

# src/api/models/ 하위이므로 프로젝트 루트는 4단계 상위
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "food_model.pickle"

READABLE_LABELS = {
    "Muscle_Gain": "Muscle Gain (근육 증가)",
    "Weight_Gain": "Weight Gain (체중 증량)",
    "Weight_Loss": "Weight Loss (체중 감량)",
    "General_Food": "General (일반 식단)",
}

_model: Optional[object] = None


def load_model() -> bool:
    global _model
    if _model is not None:
        return True
    if not MODEL_PATH.exists():
        return False
    with MODEL_PATH.open("rb") as f:
        _model = pickle.load(f)
    return True


def predict_diet_type(calories: float, protein: float, fiber: float) -> Optional[str]:
    """칼로리·단백질·식이섬유 → 식단 유형 예측 (nutriwise /predict 이식)."""
    if not load_model():
        return None
    prediction = _model.predict([[calories, protein, fiber]])[0]
    return READABLE_LABELS.get(prediction, str(prediction))
