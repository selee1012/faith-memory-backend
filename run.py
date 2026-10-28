"""로컬 실행용 엔트리포인트: `uv run python run.py`"""

import uvicorn
from app.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0" if settings.environment != "local" else "127.0.0.1",
        port=8000,
        reload=settings.environment == "local",
        access_log=False,  # 쿼리스트링 미기록 — RequestContextMiddleware가 접근 로그 담당
        log_config=None,  # app.core.logging 설정 사용
    )
