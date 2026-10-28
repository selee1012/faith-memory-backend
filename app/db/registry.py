import importlib
import pkgutil

import app.domains


def import_all_models() -> None:
    """app/domains/*/models.py 를 모두 import 해 Base.metadata에 등록한다.

    Alembic autogenerate가 모든 테이블을 인식하도록 migrations/env.py 에서 호출한다.
    """
    for module in pkgutil.iter_modules(app.domains.__path__):
        if not module.ispkg:
            continue
        try:
            importlib.import_module(f"app.domains.{module.name}.models")
        except ModuleNotFoundError as exc:
            if exc.name != f"app.domains.{module.name}.models":
                raise
