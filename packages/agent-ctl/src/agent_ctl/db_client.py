from __future__ import annotations

import typing as t

from agent_ctl.converters import convert_agent_schema_to_model

from depends import db_depends
from domain.spacetraders import agent as agent_domain
from loguru import logger as log
import sqlalchemy as sa

def load_registered_agent_by_symbol(symbol: str, engine: sa.Engine = None) -> agent_domain.RegisteredAgentModel | None:
    if not symbol:
        raise ValueError("Agent symbol cannot be None.")

    if not engine:
        log.warning("DB engine value is None. Initializing engine with app's database configuration.")
        engine: sa.Engine = db_depends.get_db_engine()

    session_pool = db_depends.get_session_pool(engine=engine)
    
    with session_pool() as session:
        repo = agent_domain.RegisteredAgentRepository(session)
        
        registered_agent: agent_domain.RegisteredAgentModel | None = repo.get_by_symbol(symbol=symbol)
        
    if not registered_agent:
        log.error(f"Could not find agent in database with symbol: {symbol}")
        return None
    else:
        log.success(f"Found registered agent matching symbol: {symbol}")
        return registered_agent


def save_registered_agent_to_db(agent: t.Union[agent_domain.RegisteredAgentIn, agent_domain.RegisterAgentResponse], engine: sa.Engine = None):
    if not agent:
        raise ValueError("agent cannot be None.")
    
    if not engine:
        log.warning("DB engine value is None. Initializing engine with app's database configuration.")
        engine: sa.Engine = db_depends.get_db_engine()
        
    log.debug(f"DB engine URL: {engine.url}")
    
    session_pool = db_depends.get_session_pool(engine=engine)
    
    with session_pool() as session:
        repo = agent_domain.RegisteredAgentRepository(session)
        
        existing_agent: agent_domain.RegisteredAgentModel | None = repo.get_by_symbol(symbol=agent.symbol)
        
        if existing_agent:
            log.warning(f"Agent '{agent.symbol}' already exists in database, returning object from database.")
            return existing_agent
        
        agent_model: agent_domain.RegisteredAgentModel = convert_agent_schema_to_model(agent=agent)

        log.debug(f"Saving agent: {agent.symbol}")
        try:
            db_agent = repo.create(agent_model)
            log.debug("Agent saved to database")
            
            return db_agent
        except Exception as exc:
            msg = f"({type(exc)}) Error saving agent '{agent.symbol}'. Details: {exc}"
            log.error(msg)
            
            raise exc
