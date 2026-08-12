"""
식단 카테고리 분류 모델 학습 스크립트 (통합본 — nutriwise 이식)

- 입력: data/korean_food_data.csv (우선) 또는 data/done_food_data.csv (USDA 폴백)
  피처: Energy_kcal, Protein_g, Fiber_g → 타겟: category
- 모델: scikit-learn RandomForestClassifier
- 출력: models/food_model.pickle (nutriwise /predict 와 동일 포맷)

재학습 명령:
    python mlops/train_classifier.py
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KOREAN_DATA_PATH = PROJECT_ROOT / "data" / "korean_food_data.csv"
USDA_DATA_PATH = PROJECT_ROOT / "data" / "done_food_data.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "food_model.pickle"

FEATURES = ["Energy_kcal", "Protein_g", "Fiber_g"]
TARGET = "category"


def main() -> None:
    # 한국 데이터 우선, 없으면 USDA 폴백
    data_path = KOREAN_DATA_PATH if KOREAN_DATA_PATH.exists() else USDA_DATA_PATH
    if not data_path.exists():
        sys.exit(f"학습 데이터가 없습니다: {KOREAN_DATA_PATH} 또는 {USDA_DATA_PATH}")
    df = pd.read_csv(data_path)
    print(f"학습 데이터: {data_path} ({df.shape[0]}건)")

    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing:
        sys.exit(f"필수 컬럼 누락: {missing}")

    X = df[FEATURES].fillna(0)
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n[평가] Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))

    PROJECT_ROOT.joinpath("models").mkdir(parents=True, exist_ok=True)
    with MODEL_PATH.open("wb") as f:
        pickle.dump(model, f)
    # DVC metrics (dvc.yaml 참조)
    import json
    with (PROJECT_ROOT / "models" / "classifier_metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"accuracy": acc, "n_samples": int(len(df))}, f, indent=2)
    print(f"모델 저장: {MODEL_PATH}")


if __name__ == "__main__":
    main()
