import uuid
from datetime import datetime
from typing import Annotated

from alembic.util.sqla_compat import compiles
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True

@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"



created_at = Annotated[datetime, mapped_column(server_default=utcnow(), default=utcnow())]
updated_at = Annotated[datetime, mapped_column(default=utcnow(), server_default=utcnow(), onupdate=utcnow(), server_onupdate=utcnow())]
pk_id = Annotated[uuid.UUID, mapped_column(primary_key=True, index=True, default=uuid.uuid4)]
