from loguru import logger as log

import db_lib
from .models import RegisteredAgentModel

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so


class RegisteredAgentRepository(db_lib.base.BaseRepository[RegisteredAgentModel]):
    """Repository for registered Spacetrader agents."""
    
    def __init__(self, session: so.Session):
        super().__init__(session, RegisteredAgentModel)
        
    def get_by_id(self, id: int):
        return self.session.query(RegisteredAgentModel).filter(RegisteredAgentModel.id == id).one_or_none()
