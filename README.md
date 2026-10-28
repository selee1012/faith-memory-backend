# faith-memory-backend

저장된 신앙 기록을 장기 기억으로 활용하는 서비스 **신앙일기(Faith-Memory)** 의 백엔드 리포지토리입니다.

> 현재의 고민과 과거의 기도·감사·묵상 기록을 연결해, **실제 기록을 근거로** 회고를 돕는 개인화 AI Agent.

## 기술 스택

Python 3.14 · FastAPI · Pydantic v2 · SQLAlchemy 2 (async) · Alembic · PostgreSQL + pgvector · uv · pytest · Ruff · mypy

## 빠른 시작

```bash
# 1. 의존성 설치 (uv 필요: brew install uv)
uv sync

# 2. 환경 변수
cp .env.example .env

# 3. DB (PostgreSQL + pgvector) 실행 및 마이그레이션
docker compose up -d db
uv run alembic upgrade head

# 4. 서버 실행 (local 환경에서는 자동 리로드)
uv run python run.py
```

- API 문서: http://127.0.0.1:8000/docs (production 환경에서는 비활성화)
- 헬스체크: `GET /health/live`, `GET /health/ready` (DB 연결 확인)

## 개발 명령어

```bash
uv run pytest                    # 테스트
uv run ruff check . && uv run ruff format .   # 린트·포맷
uv run mypy app                  # 타입 체크
uv run alembic revision --autogenerate -m "add journal entries"  # 마이그레이션 생성
docker compose --profile app up --build       # API까지 컨테이너로 실행
```

## 프로젝트 구조

```
.
├── run.py                  # 로컬 실행 엔트리포인트
├── app/
│   ├── main.py             # create_app(): 미들웨어·예외 핸들러·라우터 조립
│   ├── core/
│   │   ├── config.py       # pydantic-settings 기반 설정 (.env)
│   │   ├── logging.py      # JSON 구조화 로그, request_id 컨텍스트
│   │   ├── middleware.py   # X-Request-ID 부여 + 본문/쿼리스트링 없는 접근 로그
│   │   └── exceptions.py   # AppError 계층, 공통 오류 응답 형식
│   ├── db/
│   │   ├── base.py         # DeclarativeBase, 네이밍 규칙, UUIDv7/타임스탬프 Mixin
│   │   ├── session.py      # async 엔진·세션, 요청 단위 트랜잭션
│   │   └── registry.py     # 도메인 models 자동 import (Alembic용)
│   ├── api/
│   │   ├── deps.py         # 공통 의존성 (SessionDep, 추후 CurrentUser/AI 동의)
│   │   ├── health.py       # /health/live, /health/ready
│   │   └── router.py       # /api/v1 도메인 라우터 집합
│   ├── ai/
│   │   └── clients.py      # LLMClient / EmbeddingClient 인터페이스 (제공자 미정)
│   └── domains/            # IR 기능 영역별 모듈
│       ├── users/          # AC-01~03, 06  계정·프로필·탈퇴
│       ├── consents/       # AC-04         외부 AI 처리 동의
│       ├── journals/       # JR-01~05      일기 원문 CRUD (source of truth)
│       ├── memories/       # MM-01~05      구조화 기억·근거 연결
│       ├── search/         # SR-01~04      키워드·의미 검색, 임베딩 인덱스
│       └── reflections/    # AI-01~07      근거 기반 회고 Workflow
├── migrations/             # Alembic (0001: pgvector 확장 활성화)
└── tests/
```

### 도메인 모듈 규칙

각 `app/domains/<domain>/` 은 필요에 따라 아래 파일을 둡니다.

| 파일 | 역할 |
| --- | --- |
| `router.py` | HTTP 엔드포인트. 입력 검증·인증·동의 확인 후 service 호출 |
| `schemas.py` | Pydantic 요청/응답 스키마 |
| `service.py` | 비즈니스 로직, 트랜잭션 단위 흐름 (예: 원문 수정 → 인덱스 무효화) |
| `repository.py` | DB 접근. **모든 조회 함수는 `user_id`를 필수 인자로 받아 사용자 범위를 강제** |
| `models.py` | SQLAlchemy 모델 (자동으로 Alembic에 등록됨) |

## 설계 원칙 (IR 반영)

- **사용자 격리 (AC-02, AT-02):** 타인의 리소스 접근은 403이 아닌 `NotFoundError`(404)로 응답해 존재 여부를 숨긴다.
- **민감 로그 제한 (4.3):** 요청/응답 본문과 쿼리스트링은 로그에 남기지 않고, 422 응답에서도 사용자 입력값을 되돌려주지 않는다.
- **원문 = source of truth:** 요약·기억·임베딩은 파생 데이터이며, 원문 수정/삭제 시 무효화·재생성한다.
- **시간 분리 (4.4):** DB 저장은 UTC. 시스템 시각(`created_at`)과 사용자 기록 날짜(`entry_date`)를 분리한다.
- **AI 경계:** 도메인 코드는 `app/ai/clients.py` 인터페이스에만 의존. 동의가 없으면 `ConsentRequiredError`, LLM 장애는 `AIServiceError`.

## 다음 작업 (IR 11.2)

- [ ] 인증 방식 확정 후 `users` 모델·`CurrentUserDep` 구현
- [ ] `JournalEntry` 모델과 `/api/v1/entries` CRUD
- [ ] `UserConsent` 및 AI 기능 동의 가드
- [ ] `EntryIndex`(pgvector) 생성·무효화 흐름, `search_entries` Tool
- [ ] `POST /api/v1/reflections` 근거 기반 회고
