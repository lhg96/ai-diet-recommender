"""
BMR(기초대사량) 예측 모델 학습 스크립트 (통합본)

- 입력: data/BMR_Dataset.csv (age, weight, height, gender, BMR) — 9,000건
- 모델: RandomForestRegressor(n_estimators=100) + StandardScaler
- 출력: models/bmr_rf_model.joblib, models/bmr_scaler.joblib (+ gender LabelEncoder 정보)
- 참고: eda/bmr_analysis.ipynb 의 학습 셀(8~12)을 스크립트화한 것

재학습 명령:
    python mlops/train_bmr.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "BMR_Dataset.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "bmr_rf_model.joblib"
SCALER_PATH = MODEL_DIR / "bmr_scaler.joblib"
GENDER_ENCODER_PATH = MODEL_DIR / "bmr_gender_encoder.joblib"

FEATURES = ["age", "weight", "height", "gender"]
TARGET = "BMR"


def main() -> None:
    if not DATA_PATH.exists():
        sys.exit(f"데이터 파일이 없습니다: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print(f"데이터 로드: {DATA_PATH} ({df.shape[0]}건)")

    # 결측치 확인 및 제거 (age/weight/height/gender 결측 행은 학습에서 제외)
    print("결측치:\n", df.isnull().sum().to_string())
    df = df.dropna(subset=["age", "weight", "height", "gender", TARGET]).reset_index(drop=True)
    print(f"결측치 제거 후: {df.shape[0]}건")

    # 성별 인코딩 (Male=1, Female=0 고정 — 예측 시 동일 매핑 사용)
    gender_map = {"Male": 1, "Female": 0}
    df["gender_encoded"] = df["gender"].map(gender_map)
    if df["gender_encoded"].isnull().any():
        print("경고: 알 수 없는 gender 값이 있어 인코딩 맵을 확장합니다.")
        for val in df.loc[df["gender_encoded"].isnull(), "gender"].unique():
            gender_map[val] = max(gender_map.values()) + 1
        df["gender_encoded"] = df["gender"].map(gender_map)

    X = df[["age", "weight", "height", "gender_encoded"]]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred))
    print(f"\n[평가] RMSE: {rmse:.2f} | R2: {r2:.4f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(gender_map, GENDER_ENCODER_PATH)
    # DVC metrics (dvc.yaml 참조)
    import json
    with (MODEL_DIR / "bmr_metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"rmse": rmse, "r2": r2, "n_samples": int(len(df))}, f, indent=2)
    print(f"모델 저장: {MODEL_PATH}")
    print(f"스케일러 저장: {SCALER_PATH}")
    print(f"성별 인코딩 저장: {GENDER_ENCODER_PATH}")

    # 특성 중요도
    importance = pd.DataFrame(
        {"feature": ["나이", "체중", "신장", "성별"], "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)
    print("\n특성 중요도:\n", importance.to_string(index=False))


if __name__ == "__main__":
    main()
