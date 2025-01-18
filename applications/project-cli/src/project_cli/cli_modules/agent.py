from loguru import logger as log

import typing as t

from cyclopts import App, Group, Parameter
from depends import db_depends
import settings
import setup
import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy.exc as sa_exc
import sqlalchemy.sql as sa_sql

from domain.spacetraders import agent as agent_domain
import agent_ctl

agent_app = App(name="agent", help="CLI for managing Spacetraders agents.")

@agent_app.command(name="register")
def register_new_agent(symbol: t.Annotated[str, Parameter(name="symbol", show_default=True, help="Symbol/name to register as a new agent.")], faction: t.Annotated[str, Parameter(name="faction", show_default=True, help="Faction to register agent under. As of 1/12/2024, the only supported faction is 'COSMIC'.")] = "COSMIC"):
    if symbol is None:
        raise ValueError(f"Must provide an agent symbol.")
    
    log.info(f"Attempting to register agent: {symbol}")

    try:
        agent_dict = agent_ctl.register_agent(agent_symbol=symbol, agent_faction=faction, use_cache=True)
    except agent_domain.exc.AgentAlreadyRegisteredException as symbol_taken:
        log.error(symbol_taken)
        return
    except Exception as exc:
        msg = f"({type(exc)}) Error registering agent by symbol '{symbol}'. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.success(f"Registered agent: {symbol}")
    
    agent: agent_domain.RegisteredAgentIn = agent_domain.RegisteredAgentIn.model_validate(agent_dict)
    log.debug(f"Registered agent: {agent}")
    
    # agent_ctl.db_client.
