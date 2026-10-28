from app.core.exceptions import NotFoundError
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel, Field


async def test_liveness(client: AsyncClient) -> None:
    res = await client.get("/health/live")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


async def test_request_id_is_generated_and_propagated(client: AsyncClient) -> None:
    res = await client.get("/health/live")
    assert res.headers["X-Request-ID"]

    res = await client.get("/health/live", headers={"X-Request-ID": "trace-123"})
    assert res.headers["X-Request-ID"] == "trace-123"


async def test_invalid_request_id_is_replaced(client: AsyncClient) -> None:
    res = await client.get("/health/live", headers={"X-Request-ID": "bad id\nwith newline"})
    assert res.headers["X-Request-ID"] != "bad id\nwith newline"


async def test_validation_error_does_not_echo_user_input(app: FastAPI, client: AsyncClient) -> None:
    class Body(BaseModel):
        content: str = Field(min_length=10)

    @app.post("/_test/echo")
    async def _echo(body: Body) -> None: ...

    secret = "기도 제목"
    res = await client.post("/_test/echo", json={"content": secret})

    assert res.status_code == 422
    assert res.json()["error"]["code"] == "validation_error"
    assert secret not in res.text


async def test_not_found_error_format(app: FastAPI, client: AsyncClient) -> None:
    @app.get("/_test/missing")
    async def _missing() -> None:
        raise NotFoundError

    res = await client.get("/_test/missing")

    assert res.status_code == 404
    body = res.json()["error"]
    assert body["code"] == "not_found"
    assert body["request_id"] == res.headers["X-Request-ID"]
