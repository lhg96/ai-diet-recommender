# load data from korea FDA data from data/koreaFDA/ 
# process data researchers and institutions
# 두 데이터셋은 거의 동일한 데이터를 포함하고 있으며, 두 번째 데이터셋이 제공기관 정보만 추가로 포함하고 있음을 알 수 있습니다

import pandas as pd
import numpy as np
from pathlib import Path
import os
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any

# Get the absolute path to the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "koreaFDA"

def convert_encoding_to_utf8(file_path: Path) -> None:
    with open(file_path, 'r', encoding='euc-kr') as f:
        content = f.read()
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def load_korea_fda_data(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df

def load_and_clean_data(file_path: Path) -> pd.DataFrame:
    """CSV 파일을 로드하고 기본적인 전처리를 수행합니다."""
    print(f"\nLoading file: {file_path.name}")
    df = pd.read_csv(file_path)
    print(f"Original shape: {df.shape}")
    
    # 결측치가 있는 행의 수를 확인
    null_counts = df.isnull().sum()
    print("\nNull value counts:")
    print(null_counts[null_counts > 0])
    
    return df

def compare_columns(df1: pd.DataFrame, df2: pd.DataFrame) -> None:
    """두 데이터프레임의 컬럼을 비교합니다."""
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)
    
    print("\nColumn comparison:")
    print(f"Columns only in first dataset: {cols1 - cols2}")
    print(f"Columns only in second dataset: {cols2 - cols1}")
    print(f"Common columns: {cols1 & cols2}")

def compare_statistics(df1: pd.DataFrame, df2: pd.DataFrame, common_numeric_cols: List[str]) -> None:
    """두 데이터프레임의 통계적 특성을 비교합니다."""
    print("\nStatistical comparison:")
    for col in common_numeric_cols:
        print(f"\nComparing {col}:")
        print("\nFirst dataset:")
        print(df1[col].describe())
        print("\nSecond dataset:")
        print(df2[col].describe())

def plot_distributions(df1: pd.DataFrame, df2: pd.DataFrame, common_numeric_cols: List[str], 
                      output_dir: Path) -> None:
    """두 데이터셋의 분포를 비교하는 그래프를 생성합니다."""
    for col in common_numeric_cols:
        plt.figure(figsize=(12, 6))
        
        # KDE plot
        plt.subplot(1, 2, 1)
        sns.kdeplot(data=df1[col], label='Dataset 1', alpha=0.5)
        sns.kdeplot(data=df2[col], label='Dataset 2', alpha=0.5)
        plt.title(f'Distribution Comparison - {col}')
        plt.legend()
        
        # Box plot
        plt.subplot(1, 2, 2)
        combined_data = pd.concat([
            pd.DataFrame({'value': df1[col], 'source': 'Dataset 1'}),
            pd.DataFrame({'value': df2[col], 'source': 'Dataset 2'})
        ])
        sns.boxplot(x='source', y='value', data=combined_data)
        plt.title(f'Box Plot - {col}')
        
        plt.tight_layout()
        plt.savefig(output_dir / f'distribution_comparison_{col}.png')
        plt.close()

def main():
    # 데이터 파일 경로
    file1 = DATA_DIR / "식품의약품안전처_통합식품영양성분정보(음식)_20250408.csv"
    file2 = DATA_DIR / "전국통합식품영양성분정보_음식_표준데이터.csv"
    
    # 데이터 로드
    df1 = load_and_clean_data(file1)
    df2 = load_and_clean_data(file2)
    
    # 컬럼 비교
    compare_columns(df1, df2)
    
    # 공통된 수치형 컬럼 찾기
    numeric_types = [np.number]
    common_numeric_cols = [
        col for col in set(df1.columns) & set(df2.columns)
        if df1[col].dtype in numeric_types and df2[col].dtype in numeric_types
    ]
    
    # 통계 비교
    compare_statistics(df1, df2, common_numeric_cols)
    
    # 분포 시각화
    output_dir = PROJECT_ROOT / "docs" / "koreaFDA_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_distributions(df1, df2, common_numeric_cols, output_dir)
    
    print(f"\nAnalysis complete. Visualizations saved in: {output_dir}")

if __name__ == "__main__":
    main()
