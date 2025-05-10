from sqlalchemy.orm import Mapped

from db.lib.types import created_at, updated_at


class TimeMixin:
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
