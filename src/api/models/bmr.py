"""
BMR(기초대사량) 예측 모듈 — Random Forest 모델 로드 및 권장 칼로리 계산.

모델 파일: models/bmr_rf_model.joblib + bmr_scaler.joblib + bmr_gender_encoder.joblib
재학습:     python mlops/train_bmr.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import joblib
import numpy as np

# src/api/models/ 하위이므로 프로젝트 루트는 4단계 상위
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "bmr_rf_model.joblib"
SCALER_PATH = MODEL_DIR / "bmr_scaler.joblib"
GENDER_ENCODER_PATH = MODEL_DIR / "bmr_gender_encoder.joblib"

# 활동 계수 (Mifflin-St Jeor 기반 표준값)
ACTIVITY_FACTORS = {
    "sedentary": 1.2,     # 거의 없음 (사무직)
    "light": 1.375,       # 가벼운 활동 (주 1~3회)
    "moderate": 1.55,     # 보통 활동 (주 3~5회)
    "active": 1.725,      # 활발한 활동 (주 6~7회)
}

# 목표별 칼로리 보정 (기획서: 감량 -20%, 증량 +15%, 근육증가 유지+단백질↑)
GOAL_ADJUSTMENTS = {
    "weightloss": 0.80,   # -20%
    "weightgain": 1.15,   # +15%
    "musclegain": 1.00,   # 유지 (단백질 비중 상향은 추천 카드에서 처리)
}

_model: Optional[object] = None
_scaler: Optional[object] = None
_gender_map: Dict[str, int] = {"Male": 1, "Female": 0}


def load_model() -> bool:
    """모델 로드. 성공 시 True."""
    global _model, _scaler, _gender_map
    if _model is not None:
        return True
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        return False
    _model = joblib.load(MODEL_PATH)
    _scaler = joblib.load(SCALER_PATH)
    if GENDER_ENCODER_PATH.exists():
        _gender_map = joblib.load(GENDER_ENCODER_PATH)
    return True


def predict_bmr(age: float, weight: float, height: float, gender: str) -> Optional[float]:
    """BMR 예측. 모델 없으면 None."""
    if not load_model():
        return None

    gender_encoded = _gender_map.get(gender, 0.5)  # Male=1, Female=0, 기타=0.5
    features = np.array([[age, weight, height, gender_encoded]])
    scaled = _scaler.transform(features)
    return float(_model.predict(scaled)[0])


def calculate_daily_calories(
    bmr: float, activity: str = "light", goal: str = "weightloss"
) -> Dict[str, float]:
    """BMR → TDEE(활동계수) → 목표 보정 칼로리 계산."""
    factor = ACTIVITY_FACTORS.get(activity, ACTIVITY_FACTORS["light"])
    tdee = bmr * factor
    adjustment = GOAL_ADJUSTMENTS.get(goal, 1.0)
    goal_calories = tdee * adjustment
    return {
        "bmr": round(bmr, 1),
        "activity_factor": factor,
        "tdee": round(tdee, 1),
        "goal_calories": round(goal_calories, 1),
    }
