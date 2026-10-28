"""공통 예외와 오류 응답 형식.

모든 오류는 {"error": {"code", "message", "request_id"}} 형태로 응답한다.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import request_id_ctx

logger = logging.getLogger(__name__)


class AppError(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "bad_request"
    message: str = "잘못된 요청입니다."

    def __init__(self, message: str | None = None, *, code: str | None = None) -> None:
        self.message = message or self.message
        self.code = code or self.code
        super().__init__(self.message)


class NotFoundError(AppError):
    """리소스가 없거나 *다른 사용자의 소유*인 경우.

    IR AT-02: 타인의 기록에 대해 403을 주면 존재 여부가 노출되므로 항상 404로 응답한다.
    """

    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    message = "요청한 리소스를 찾을 수 없습니다."


class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    message = "인증이 필요합니다."


class ConsentRequiredError(AppError):
    """IR AC-04 / AT-07: 외부 AI 처리 동의가 없으면 AI 기능 실행을 차단한다."""

    status_code = status.HTTP_403_FORBIDDEN
    code = "ai_consent_required"
    message = "AI 기능을 사용하려면 외부 AI 처리 동의가 필요합니다."


class AIServiceError(AppError):
    """IR AI-07: LLM 오류/타임아웃. 기록 데이터는 유실되지 않으며 재시도 가능함을 알린다."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "ai_unavailable"
    message = "AI 응답을 받지 못했습니다. 잠시 후 다시 시도해 주세요."


def _error_body(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "request_id": request_id_ctx.get(), **extra}
    }


async def _app_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return JSONResponse(status_code=exc.status_code, content=_error_body(exc.code, exc.message))


async def _validation_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    # FastAPI 기본 응답은 'input'에 사용자가 보낸 값(일기 원문)을 그대로 되돌려주므로 제거한다.
    details = [
        {"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=_error_body("validation_error", "입력값이 올바르지 않습니다.", details=details),
    )


async def _unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_error", extra={"error_type": type(exc).__name__})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body("internal_error", "서버 오류가 발생했습니다."),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(Exception, _unhandled_error_handler)
