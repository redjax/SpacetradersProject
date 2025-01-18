from __future__ import annotations

from .models import RegisteredAgentModel

import db_lib
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

class RegisteredAgentRepository(db_lib.base.BaseRepository[RegisteredAgentModel]):
    """Repository for registered Spacetrader agents."""
    
    def __init__(self, session: so.Session):
        super().__init__(session, RegisteredAgentModel)
        
    def get_by_id(self, id: int) -> RegisteredAgentModel | None:
        return self.session.query(RegisteredAgentModel).filter(RegisteredAgentModel.agent_id == id).one_or_none()
    
    def get_by_symbol(self, symbol: str) -> RegisteredAgentModel | None:
        return self.session.query(RegisteredAgentModel).filter(RegisteredAgentModel.symbol == symbol).one_or_none()

    def get_by_faction(self, faction: str = "COSMIC") -> list[RegisteredAgentModel] | None:
        return self.session.query(RegisteredAgentModel).filter(RegisteredAgentModel.faction == faction).all()
        
    def get_by_headquarters(self, headquarters: str) -> list[RegisteredAgentModel] | None:
        return self.session.query(RegisteredAgentModel).filter(RegisteredAgentModel.headquarters == headquarters).all()

    def get_all_agents(self) -> list[RegisteredAgentModel] | None:
        return self.session.query(RegisteredAgentModel).all()
