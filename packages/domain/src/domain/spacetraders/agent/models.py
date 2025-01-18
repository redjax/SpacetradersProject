from __future__ import annotations

import db_lib
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.types import JSON

class RegisteredAgentModel(db_lib.Base, db_lib.TimestampMixin):
    """SQLAlchemy database model class for Spacetraders registered agent.
    
    Params:
        agent_id (int): Auto-generated index ID in the database. Note: You do not need to, nor should you, pass a value for this.
            The database will automatically generate an ID when creating the entity.
        symbol (str): The agent's symbol/username.
        faction (str): (Default: "COSMIC") The registered agent's faction.
        headquarters (str): The agent's HQ name.
        token (str): The agent's API token (this is a private/secret value, make sure to store it securely).
        full_response (dict): The full JSON response from the "POST register agent" request.

    """

    __tablename__ = "registeredAgent"

    agent_id: so.Mapped[db_lib.annotated.INT_PK]

    account_id: so.Mapped[db_lib.annotated.STR_255]
    symbol: so.Mapped[str] = so.mapped_column(sa.VARCHAR(14), unique=True)
    faction: so.Mapped[db_lib.annotated.STR_255]
    headquarters: so.Mapped[db_lib.annotated.STR_255]
    token: so.Mapped[db_lib.annotated.STR_255]
    # full_response: so.Mapped[bytes] = so.mapped_column(sa.LargeBinary)
    full_response: so.Mapped[dict] = so.mapped_column(JSON)
