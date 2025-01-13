from __future__ import annotations

from typing import Optional

import db_lib
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.types import JSON

class RegisteredAgentModel(db_lib.Base, db_lib.TimestampMixin):
    __tablename__ = "registeredAgent"

    agent_id: so.Mapped[db_lib.annotated.INT_PK]

    account_id: so.Mapped[db_lib.annotated.STR_255]
    symbol: so.Mapped[str] = so.mapped_column(sa.VARCHAR(14), unique=True)
    faction: so.Mapped[db_lib.annotated.STR_255]
    headquarters: so.Mapped[db_lib.annotated.STR_255]
    token: so.Mapped[db_lib.annotated.STR_255]
    # full_response: so.Mapped[bytes] = so.mapped_column(sa.LargeBinary)
    full_response: so.Mapped[dict] = so.mapped_column(JSON)
