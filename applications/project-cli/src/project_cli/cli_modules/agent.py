from __future__ import annotations

import typing as t

import agent_ctl
from cyclopts import App, Group, Parameter
from depends import db_depends
from domain.spacetraders import agent as agent_domain
from loguru import logger as log
import settings
import setup
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so
import sqlalchemy.sql as sa_sql

agent_app = App(name="agent", help="CLI for managing Spacetraders agents.")

@agent_app.command(name="register")
def register_new_agent(symbol: t.Annotated[str, Parameter(name="symbol", show_default=True, help="Symbol/name to register as a new agent.")] | None = None, faction: t.Annotated[str, Parameter(name="faction", show_default=True, help="Faction to register agent under. As of 1/12/2024, the only supported faction is 'COSMIC'.")] = "COSMIC", random: t.Annotated[bool, Parameter(name="random", help="Set to true if you want to register the agent with a random name.")] = False):
    if symbol is None:
        if random:
            log.warning(f"Detected --random flag. If you passed an agent symbol, it will be overridden by a random one.")
            symbol: str = agent_ctl.get_random_agent_symbol()
        else:
            raise ValueError(f"Must provide an agent symbol.")
    
    log.info(f"Attempting to register agent: {symbol}")

    try:
        agent_dict: dict = agent_ctl.register_agent(agent_symbol=symbol, agent_faction=faction, use_cache=True)
    except agent_domain.exc.AgentAlreadyRegisteredException as symbol_taken:
        log.error(symbol_taken)
        return
    except Exception as exc:
        msg = f"({type(exc)}) Error registering agent by symbol '{symbol}'. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.success(f"Registered agent: {symbol}")
    
    agent_response: agent_domain.RegisterAgentResponse = agent_ctl.convert_register_agent_res_dict_to_class(agent_dict)
    
    agent_in: agent_domain.RegisteredAgentIn = agent_ctl.convert_http_response_schema_to_agent_in_schema(registered_agent=agent_response)
    log.debug(f"Registered agent: {agent_in}")

    log.debug(f"Saving agent '{symbol}' to database")
    try:
        db_agent: agent_domain.RegisteredAgentModel = agent_ctl.db_client.save_registered_agent_to_db(agent=agent_in)
        
        if db_agent:
            log.success("Agent saved to database.")
    except Exception as exc:
        msg = f"({type(exc)}) Error saving agent '{symbol}' to database. Details: {exc}"
        log.error(msg)
        
        raise exc