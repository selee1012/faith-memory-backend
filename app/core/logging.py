"""구조화 로그 설정.

IR 4.3 '민감 로그 제한': 일기 원문·기도 내용·토큰은 로그에 남기지 않는다.
- 요청/응답 본문과 쿼리스트링은 기록하지 않는다 (검색 키워드도 민감 정보일 수 있음).
- 로그 메시지에 사용자 입력을 직접 포함하지 말고, ID·상태·지연 등 메타데이터만 남긴다.
"""

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

_RESERVED_ATTRS = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {
    "message",
    "color_message",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_ctx.get(),
        }
        # logger.info("...", extra={"latency_ms": 12}) 형태의 구조화 필드
        payload.update({k: v for k, v in record.__dict__.items() if k not in _RESERVED_ATTRS})
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())

    # uvicorn 기본 access log는 쿼리스트링을 남기므로 끄고,
    # RequestContextMiddleware가 대신 기록한다.
    logging.getLogger("uvicorn.access").disabled = True
    for name in ("uvicorn", "uvicorn.error"):
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
