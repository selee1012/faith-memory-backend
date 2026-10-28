from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db_session

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

# TODO(AC-01): 인증 방식 확정 후 CurrentUserDep 추가.
#   모든 기록·기억·회고 조회는 current_user.id 로 범위를 강제한다 (AC-02).
# TODO(AC-04): AI 기능 라우터에는 RequireAIConsentDep 를 걸어 동의가 없으면 ConsentRequiredError.
