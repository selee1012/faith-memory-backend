from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class LLMUsage:
    """AIExecutionLog 계측용 (IR 4.2 비용·지연). 원문은 포함하지 않는다."""

    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


@dataclass(frozen=True)
class LLMResult:
    output: dict[str, Any]  # Structured Output (JSON 스키마 검증 후)
    usage: LLMUsage


class LLMClient(Protocol):
    async def generate_structured(
        self,
        *,
        system: str,
        user: str,
        output_schema: dict[str, Any],
    ) -> LLMResult:
        """검색된 일기 본문은 `user` 안에서 데이터로만 전달한다 (IR 4.3 프롬프트 인젝션 대응).

        타임아웃·일시 오류는 유한 재시도 후 AIServiceError 로 변환한다 (IR AI-07).
        """
        ...


class EmbeddingClient(Protocol):
    @property
    def model_version(self) -> str: ...  # EntryIndex.index_version 과 비교해 재색인 판단

    async def embed(self, texts: Sequence[str]) -> list[list[float]]: ...
