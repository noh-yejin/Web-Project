# 💫 AI 감정 저널 웹 애플리케이션

사용자가 자신의 감정과 생각을 자유롭게 기록할 수 있도록 돕는 **AI 기반 감정 저널**입니다.  
기록된 데이터를 바탕으로 감정의 흐름을 시각화하고, 이에 따른 맞춤형 조언과 추천을 제공하여 **정서적 안정을 지원**합니다.

---

## 💡 주요 기능

- 감정 및 생각을 기록할 수 있는 **저널 기능**
- **LLaMA 3-8B 모델 기반 감정 분석**, 맞춤형 조언 및 정서적 회복을 위한 활동 추천 제공
- **Chart.js**를 활용한 주간 감정 추세 시각화 및 분석, 피드백 제공
- 저널 기반 **감정 점수 산출 및 감정 달력 시각화** (이모티콘 및 색상 매핑)

---

## 🛠 사용 기술

| 분류 | 기술 |
|------|------|
| **백엔드** | FastAPI, MCP Server, LLaMA 3-8B (OpenRouter API) |
| **프론트엔드** | HTML, CSS, JavaScript, Chart.js |
| **데이터베이스** | Supabase |
| **기타** | 감정 점수 시스템, 감정 달력, 감정 기반 추천 기능 |

---

## 🚀 실행 방법

### 1. 의존성 설치
`pip install -r requirements.txt`
### 2. 환경 변수 설정
프로젝트 루트에 .env 파일 생성 후 다음 내용을 입력하세요:
```
OPENROUTER_API_KEY=your_openrouter_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
```
### 3. 서버 실행
상위 폴더에서 다음 명령어 실행
`uvicorn backend.app:app --reload`

---

## 📂 프로젝트 폴더 구조 예시
```
Web-Project /
├── main.py                # FastAPI 메인 서버 파일
├── backend/               # 백엔드 관련 모듈 (예: supabase_client.py)
├── frontend/                # 프론트엔드 정적 파일 (HTML, CSS, JS)
│   ├── html
│   ├── css
│   └── js
├── requirements.txt       # 의존성 목록 파일
├── .env                   # 환경 변수 파일
└── README.md              # 프로젝트 설명 파일
```
