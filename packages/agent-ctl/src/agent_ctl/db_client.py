from loguru import logger as log

import typing as t
from domain.spacetraders import agent as agent_domain
from agent_ctl.converters import convert_agent_schema_to_model
from depends import db_depends

import sqlalchemy as sa

def load_registered_agent_by_symbol(symbol: str) -> agent_domain.RegisteredAgentOut:
    if not symbol:
        raise ValueError("Agent symbol cannot be None.")

    session_pool = db_depends.get_session_pool()
    
    with session_pool() as session:
        repo = agent_domain.RegisteredAgentRepository(session)
        
        registered_agent: agent_domain.RegisteredAgentModel | None = repo.get_by_symbol(symbol=symbol)
        
    if not registered_agent:
        log.error(f"Could not find agent in database with symbol: {symbol}")
        return None
    else:
        log.success(f"Found registered agent matching symbol: {symbol}")
        return registered_agent


def save_registered_agent_to_db(agent: t.Union[agent_domain.RegisteredAgentIn, agent_domain.RegisterAgentResponse], engine: sa.Engine = db_depends.get_db_engine()):
    if not agent:
        raise ValueError("agent cannot be None.")
    
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
