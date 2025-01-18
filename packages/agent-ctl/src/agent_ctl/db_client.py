from loguru import logger as log

from domain.spacetraders import agent as agent_domain
from depends import db_depends

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


def save_registered_agent_to_db(agent: agent_domain.RegisteredAgentIn):
    if not agent:
        raise ValueError("agent cannot be None.")
    
    session_pool = db_depends.get_session_pool()
    
    with session_pool() as session:
        repo = agent_domain.RegisteredAgentRepository(session)
        
        

        log.debug(f"Saving agent: {agent.symbol}")
        try:
            repo.create(agent_model)
        except Exception as exc:
            msg = f"({type(exc)}) Error saving agent '{agent.symbol}'. Details: {exc}"
            log.error(msg)
            
            raise exc
