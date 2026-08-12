"""
한국 식품 데이터 EDA — nutriwise-diet-recommender/eda.py 를 한국 데이터(korean_food_data.csv)로 이식.

실행:
    python eda/eda.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # 헤드리스 환경 대응 (플롯을 파일로 저장)
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "korean_food_data.csv"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "eda"
TARGET_CATEGORY = "Weight_Loss"
NUMERIC_COLUMNS = ["Energy_kcal", "Protein_g", "Fat_g", "Sugar_g", "Fiber_g", "Iron_mg", "Calcium_mg"]


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    missing = [col for col in NUMERIC_COLUMNS + ["category", "Descrip"] if col not in df.columns]
    if missing:
        raise ValueError(f"다음 필수 컬럼이 없습니다: {', '.join(missing)}")
    return df


def describe_target(df: pd.DataFrame) -> pd.DataFrame:
    target = df[df["category"] == TARGET_CATEGORY]
    if target.empty:
        raise ValueError(f"{TARGET_CATEGORY} 카테고리 데이터가 없습니다.")

    print("▶ Weight Loss 식품 통계")
    print(target[NUMERIC_COLUMNS].describe())

    print("\n▶ Top 10 저칼로리 Weight Loss 식품")
    print(target.nsmallest(10, "Energy_kcal")[["Descrip", "Energy_kcal", "Protein_g", "Fat_g", "Sugar_g"]])
    return target


def plot_distributions(df: pd.DataFrame, target: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x="category", y="Energy_kcal")
    plt.title("카테고리별 칼로리 분포")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "calories_by_category.png", dpi=120)
    plt.close()

    plt.figure(figsize=(10, 6))
    corr = target[NUMERIC_COLUMNS].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Weight Loss 식품 영양소 상관관계")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "weight_loss_corr.png", dpi=120)
    plt.close()

    print(f"\n시각화 저장 완료: {OUTPUT_DIR}")


def main() -> None:
    df = load_data(DATA_PATH)
    print(f"전체 데이터: {df.shape[0]}개 음식, 카테고리: {df['category'].value_counts().to_dict()}")
    target = describe_target(df)
    plot_distributions(df, target)


if __name__ == "__main__":
    main()
