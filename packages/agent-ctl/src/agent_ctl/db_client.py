from __future__ import annotations

import typing as t

from agent_ctl.converters import convert_agent_schema_to_model, convert_http_response_schema_to_agent_in_schema

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


def save_multiple_registered_agents_to_db(agents: list[t.Union[agent_domain.RegisteredAgentIn, agent_domain.RegisterAgentResponse]], engine: sa.Engine = None):
    if not agents:
        raise ValueError("agents list cannot be None.")
    if not isinstance(agents, list) and len(agents) > 0:
        raise ValueError("agents list must be a list object and have 1 or more objects in it.")
    
    if not engine:
        log.warning("DB engine value is None. Initializing engine with app's database configuration.")
        engine: sa.Engine = db_depends.get_db_engine()
        
    log.debug(f"DB engine URL: {engine.url}")
    
    session_pool = db_depends.get_session_pool(engine=engine)
    
    _agents: list[agent_domain.RegisteredAgentIn] = []
    for a in agents:
        log.debug(f"Converting agent: {a}")
        if isinstance(a, agent_domain.RegisterAgentResponse):
            try:
                _a = convert_http_response_schema_to_agent_in_schema(a)
                log.debug(f"Converted agent to RegisteredAgentResponse object: {_a}")
                _agents.append(_a)
            except Exception as exc:
                msg = f"({type(exc)}) Error converting object to RegisteredAgentResponse. Details: {exc}"
                log.error(msg)
                
                continue
        elif isinstance(a, agent_domain.RegisteredAgentIn):
            log.debug("Agent is already of type RegisteredAgentIn")
            _agents.append(a)
            continue
        else:
            log.warning(f"Agent is not a RegisterAgentResponse object, it is a ({type(a)}). Skipping attempt at conversion")
            continue
    log.debug(f"Length of converted agents: {len(_agents)}")

    
    with session_pool() as session:
        repo = agent_domain.RegisteredAgentRepository(session)
        
        symbols: list[str] = [a.symbol for a in _agents]
        existing_symbols: list[str] | None = []
        
        log.debug(f"Searching database for [{len(symbols)}] agent(s) by symbol")
        existing_agents: list[agent_domain.RegisteredAgentModel] = repo.get_multiple_by_symbol(symbols=symbols)
        
        if not existing_agents or (isinstance(existing_agents, list) and len(existing_agents) > 0):
            log.debug("All agents in incoming list are new.")
        else:
            existing_symbols = [a.symbol for a in existing_agents]
        
        agent_models: list[agent_domain.RegisteredAgentModel] = []
        
        for agent_schema in _agents:
            log.debug(f"Converting agent to database model: {agent_schema}")
            if agent_schema.symbol in existing_symbols:
                log.warning(f"Agent '{agent_schema.symbol}' already exists in the database. Skipping.")
                continue
            else:
                log.debug(f"Agent symbol '{agent_schema.symbol}' does not exist in the database. Continuing")

            try:
                _model: agent_domain.RegisteredAgentModel = convert_agent_schema_to_model(agent_schema)
                # log.debug(f"Agent model: {_model.__dict__}")
                agent_models.append(_model)
            except Exception as exc:
                msg = f"({type(exc)}) Error converting agent schema to RegisteredAgentModel. Details: {exc}"
                log.error(msg)
                
                continue
            
        log.debug(f"Converted [{len(agent_models)}] agent schema(s) to RegisteredAgentModel object(s).")
        
        saved_agents: list[agent_domain.RegisteredAgentModel] = []
        
        log.info(f"Saving [{len(agent_models)}] agent(s) to the database.")
        try:
            saved_agents = repo.create_all(agent_models)
            log.debug(f"Saved [{len(saved_agents)}] to database")
            return saved_agents
        except Exception as exc:
            msg = f"({type(exc)}) Error saving multiple agents to database. Details: {exc}"
            log.error(msg)
            
            raise exc
        # for agent_model in agent_models:
        #     try:
        #         db_agent = repo.create(agent_model)
        #         log.debug(f"DB agent ({type(db_agent)}): {db_agent}")
        #         saved_agents.append(db_agent)
        #     except Exception as exc:
        #         msg = f"({type(exc)}) Error saving agent to database. Details: {exc}"
        #         log.error(msg)
                
        #         continue
            
        # log.info(f"Saved [{len(saved_agents)}] to database")
    
    return saved_agents
