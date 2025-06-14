# 세종시 스마트시티 AI 다이어트 식단 추천 서비스

## 1. 프로젝트 개요

### 프로젝트 설명
- **명칭**: 세종시 스마트시티 헬스 데이터 기반 MLOps AI 다이어트 식단 추천 서비스
- **목표**: 세종시 공공 헬스케어 인프라를 활용한 개인 맞춤형 AI 식단 추천 시스템 구축

### 핵심 가치
- ✅ **시민 건강 개선**: 비만율 감소, 건강 식습관 유도
- ✅ **스마트시티 활용**: 세종시 인프라(음식점, 운동시설, 보건소)와 위치 기반 연계
- ✅ **AI 기반 자동화**: 개인 맞춤 식단 추천 및 지속적인 개선
- ✅ **MLOps 적용**: 실시간 재학습, 성능 모니터링, 모델 실험 관리
- ✅ **문서화 제공**: 사용자와 기관에서 활용 가능한 문서형 레시피 및 건강 리포트

### 주요 기능
1. **사용자 입력**
   - 키, 몸무게, 성별, 목표 체중
   - 식습관(채식/비건, 자주 먹는 음식), 알레르기, 활동량
   - 지역: 세종시 내 거주지(읍/면/동 단위)

2. **AI 기반 맞춤 식단 추천**
   - 하루 3식 기준 식단 자동 구성
   - 탄수화물, 단백질, 지방 비율 자동 계산
   - 1일~7일 주간 식단 제공

3. **문서 생성**
   - PDF/Excel 형식의 식단표
   - 조리법, 재료, 칼로리 정보 포함
   - 다운로드 링크 또는 이메일 전송

4. **위치 기반 서비스**
   - 추천 식단에 적합한 지역 음식점 정보
   - 헬스장/보건소 지도 연동 및 QR코드 제공

## 2. 기술 스택

### 백엔드
- **Framework**: FastAPI
- **AI/ML**: 
  - LightGBM (맞춤형 식단 추천)
  - KNN (유사 레시피 추천)
  - TF-IDF, Cosine Similarity (레시피 유사도 계산)

### MLOps
- **데이터 버전 관리**: DVC
- **실험 관리**: MLflow
- **모니터링**: Prometheus + Grafana
- **CI/CD**: GitHub Actions
- **컨테이너화**: Docker

### 프론트엔드
- **UI**: Gradio
- **문서 생성**: Jinja2 + WeasyPrint (PDF/Excel 생성)

### 데이터 소스
- USDA FoodData Central (영양소 정보)
- Recipe1M+ (레시피 데이터)
- OpenFoodFacts (식품 성분 정보)
- 세종시 공공데이터 (위치 기반 정보)

## 3. 설치 및 실행

### 환경 설정
```bash
# 저장소 클론
git clone https://github.com/your-org/sejong-diet-recommender.git
cd sejong-diet-recommender

# 가상환경 설정
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### DVC 설정
```bash
# 데이터 버전 관리 초기화
dvc init
dvc remote add -d storage s3://your-bucket/dvc-storage
dvc pull data/raw
```

### 서버 실행
```bash
# MLflow 서버 시작
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./models \
  --host 0.0.0.0 --port 5000

# FastAPI 서버 실행
python run.py
```

## 4. 개발 가이드

### API 엔드포인트
- `GET /`: 메인 페이지
- `POST /recommend`: 식단 추천 API
- `GET /report/{user_id}`: PDF/Excel 리포트 생성

### ML 모델 개발
1. 데이터 전처리 (`src/preprocessing/`)
2. 모델 학습 (`src/training/`)
3. MLflow로 실험 관리
4. Model Registry에 등록

### MLOps 파이프라인
1. GitHub Actions으로 CI/CD 구성
2. DVC로 데이터/모델 버전 관리
3. Prometheus/Grafana로 모니터링

## 5. 프로젝트 구조
```
sejong-diet-recommender/
├── data/                   # 데이터 관리 (DVC)
│   ├── raw/               # 원본 데이터
│   └── processed/         # 전처리된 데이터
├── models/                # 학습된 모델 (MLflow)
├── mlops/                 # MLOps 설정
│   ├── dvc.yaml          # DVC 파이프라인
│   ├── mlflow/           # MLflow 설정
│   └── github-actions/   # CI/CD 워크플로우
├── src/
│   ├── api/              # FastAPI 서버
│   ├── preprocessing/    # 데이터 전처리
│   ├── training/        # 모델 학습
│   ├── inference/       # 추론 로직
│   └── utils/          # 유틸리티
├── docs/                # 문서 템플릿
└── docker/             # Docker 설정
```

## 6. 라이선스
MIT License

## 7. 기여 방법
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
