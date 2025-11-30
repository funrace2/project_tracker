# 📋 Project Tracker

> 심플한 프로젝트 관리 도구

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-red.svg)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-8.4+-orange.svg)](https://www.mysql.com/)

## 📖 프로젝트 개요

**Project Tracker**는 개발자가 여러 프로젝트를 효율적으로 관리할 수 있도록 만든 경량 도구입니다.

### 💡 만든 이유

부트캠프를 하면서 이런 불편함이 있었어요:
- 프로젝트별 태스크가 여기저기 흩어져 있음
- 진행 상황을 한눈에 파악하기 어려움
- 회고를 제대로 기록하지 못함
- 기존 도구들은 너무 복잡하거나 단순함

그래서 **딱 필요한 기능만** 넣은 도구를 만들었습니다!

---

## ✨ 주요 기능

### 📊 대시보드
- 프로젝트 진행률을 한눈에 확인
- Plotly 인터랙티브 차트
- 메트릭 카드로 주요 지표 표시

### 📋 Kanban 보드
- To Do / In Progress / Done
- 클릭으로 상태 변경
- 우선순위 및 태그 시스템

### ✅ 태스크 관리
- 빠른 태스크 추가
- 체크리스트 기능
- 마감일 및 예상 시간 설정

### 📅 마일스톤
- 주요 체크포인트 관리
- 완료 여부 체크
- 목표 날짜 추적

### 📝 회고 (KPT)
- Keep / Problem / Try
- 학습 내용 기록
- 프로젝트별 저장

---

## 🚀 빠른 시작

### 1. 환경 준비

```bash
# Python 3.13+ 필요
python --version

# MySQL 8.4+ 필요
mysql --version
```

### 2. 프로젝트 설정

```bash
# 프로젝트 클론 (또는 다운로드)
git clone <repository-url>
cd project_tracker

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. 데이터베이스 설정

```bash
# MySQL 접속
mysql -u root -p

# 데이터베이스 생성
CREATE DATABASE project_tracker;
exit;

# 스키마 생성 (database/schema.sql 파일 실행)
mysql -u root -p project_tracker < database/schema.sql
```

### 4. 비밀 정보 설정

`.streamlit/secrets.toml` 파일 생성:

```bash
# 예시 파일을 복사
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# secrets.toml 파일을 열어서 실제 MySQL 비밀번호 입력
```

`.streamlit/secrets.toml` 내용:

```toml
[mysql]
host = "localhost"
port = 3306
user = "root"
password = "your_password_here"  # 실제 비밀번호로 변경
database = "project_tracker"
```

### 5. 실행!

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 📁 프로젝트 구조

```
project_tracker/
├── app.py                      # 메인 애플리케이션
├── config.py                   # 설정 관리
├── db_manager.py               # 데이터베이스 관리
├── utils.py                    # 유틸리티 함수
├── requirements.txt            # 패키지 의존성
├── README.md                   # 이 파일
│
├── .streamlit/                 # Streamlit 설정
│   ├── secrets.toml.example   # 비밀 정보 예시 파일
│   └── secrets.toml           # 비밀 정보 (직접 생성 필요)
│
├── components/                 # UI 컴포넌트
│   ├── __init__.py            # 컴포넌트 초기화
│   ├── sidebar.py             # 사이드바 (프로젝트 선택)
│   ├── project_forms.py       # 프로젝트 생성/수정 폼
│   └── main_content.py        # 메인 콘텐츠 렌더링
│
├── views/                      # 화면 뷰
│   ├── __init__.py            # 뷰 초기화
│   ├── dashboard.py           # 대시보드 화면
│   ├── kanban.py              # 칸반 보드 화면
│   └── retrospective.py       # 회고 화면
│
├── database/                   # 데이터베이스
│   ├── schema.sql             # 테이블 스키마
│   └── sample_data.sql        # 샘플 데이터
│
└── docs/                       # 문서
    ├── 01_프로젝트_기획서.md
    ├── 02_기능명세서.md
    └── 03_데이터베이스_설계서.md
```

---

## 🛠️ 기술 스택

- **Frontend**: Streamlit (Python 웹 프레임워크)
- **Charts**: Plotly (인터랙티브 차트)
- **Database**: MySQL 8.4+
- **Language**: Python 3.13+

### 주요 패키지

```txt
streamlit==1.45.1          # 웹 프레임워크
pandas==2.2.3              # 데이터 처리
plotly==5.24.1             # 차트 시각화
mysql-connector-python==9.5.0  # MySQL 연결
```

> **참고**: 전체 패키지 목록은 [requirements.txt](requirements.txt) 참조

---

## 💡 사용 방법

### 1. 프로젝트 생성

1. 사이드바에서 "➕ 새 프로젝트" 클릭
2. 프로젝트명, 시작일, 목표일 입력
3. "생성" 버튼 클릭

### 2. 태스크 추가

**빠른 추가** (Kanban 보드):
- 상단 입력창에 제목 입력 후 Enter

**상세 추가**:
- "새 태스크" 버튼 클릭
- 모든 정보 입력 (제목, 설명, 우선순위 등)

### 3. 태스크 이동

- 각 카드의 버튼 클릭
- To Do → In Progress → Done

### 4. 진행률 확인

- 대시보드 탭에서 차트로 확인
- 메트릭 카드로 빠른 확인

### 5. 회고 작성

- 회고 탭 이동
- KPT 작성
- 저장 버튼 클릭

---

## 📅 개발 일정 (7일)

- **Day 1-2**: 환경 설정 + DB 구축
- **Day 3-4**: Kanban 보드 + 태스크 관리
- **Day 5**: 대시보드 + 차트
- **Day 6**: 회고 + UI 개선
- **Day 7**: 테스트 + 발표 준비

---

## 🐛 문제 해결

### MySQL 연결 오류
```bash
# MySQL 서버 실행 확인
mysql -u root -p

# secrets.toml 파일 확인
cat .streamlit/secrets.toml
```

### 패키지 import 오류
```bash
# 가상환경 확인
which python  # venv/bin/python 이어야 함

# 패키지 재설치
pip install -r requirements.txt
```

### 포트 충돌
```bash
# 다른 포트로 실행
streamlit run app.py --server.port 8502
```

---

## 📚 문서

상세 문서는 `docs/` 폴더 참조:

- [프로젝트 기획서](docs/01_프로젝트_기획서.md)
- [기능 명세서](docs/02_기능명세서.md)
- [데이터베이스 설계서](docs/03_데이터베이스_설계서.md)

---

## 👤 개발자

**구현모**
- iOS 앱 개발 부트캠프 수강 중
- AI 분석 기반 감정 일기 앱: Mentory 개발 중
