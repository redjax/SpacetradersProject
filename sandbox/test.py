from __future__ import annotations

import agent_ctl
import core_utils
import core_utils.hash_utils
import core_utils.uuid_utils
import db_lib
import http_lib
from loguru import logger as log
import settings
import setup
from domain.spacetraders import agent as agent_domain

demo_db_dict = {
    "drivername": "sqlite+pysqlite",
    "username": None,
    "password": None,
    "host": None,
    "port": None,
    "database": ".db/demo.sqlite3",
}


def return_engine(db_conf: dict = demo_db_dict, echo: bool = False):
    db_uri = db_lib.get_db_uri(**db_conf)
    engine = db_lib.get_engine(url=db_uri, echo=echo)

    return engine

def demo_register_single_agent():
    session_pool = db_lib.get_session_pool(engine=return_engine())
    
    log.info("Testing register agent")
    try:
        register_agent_response = agent_ctl.register_agent(
            agent_symbol=core_utils.uuid_utils.get_rand_uuid(
                characters=14, as_str=True
            ),
            use_cache=True,
        )
    except Exception as exc:
        msg = f"({type(exc)}) Error registering demo agent. Details: {exc}"
        log.error(msg)

        raise exc

    log.info(f"Registered agent: {register_agent_response}")

    with session_pool() as session:
        repo = agent_domain.RegisteredAgentRepository(session)

        log.info("Converting register agent response to database model")
        try:
            agent_model = agent_domain.RegisteredAgentModel(
                account_id=register_agent_response["data"]["agent"]["accountId"],
                symbol=register_agent_response["data"]["agent"]["symbol"],
                faction=register_agent_response["data"]["agent"]["startingFaction"],
                headquarters=register_agent_response["data"]["agent"]["headquarters"],
                token=register_agent_response["data"]["token"],
                full_response=register_agent_response,
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error converting registered agent to RegisteredAgentModel. Details: {exc}"
            log.error(msg)
            
            raise exc
        
        log.info("Saving registered agent to database.")
        try:
            repo.create(agent_model)
        except Exception as exc:
            msg = f"({type(exc)}) Error creating agent in database. Details: {exc}"
            log.error(msg)
            
            raise exc


def demo_register_multiple_agents(num_agents: int = 3):
    session_pool = db_lib.get_session_pool(engine=return_engine())
    
    _agents: list[dict] = []
    loops: int = 0
    
    while loops < num_agents:
        log.info(f"Creating agent [{loops}/{num_agents}]")
        agent_symbol = core_utils.uuid_utils.get_rand_uuid(
                characters=14, as_str=True
            )
        agent_faction = "COSMIC"
        agent = {"symbol": agent_symbol, "faction": agent_faction}
        _agents.append(agent)
        
        loops += 1
        
    log.info(f"Generated [{len(_agents)}] agent(s)")
    
    log.info(f"Registering [{len(_agents)}] agent(s)")
    try:
        registered_agents = agent_ctl.register_multiple_agents(agents=_agents, use_cache=True)
    except Exception as exc:
        msg = f"({type(exc)}) Error registering multiple agents. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.info(f"Successfully registered [{len(registered_agents)}] agent(s) with the Spacetraders API.")
    
    saved_agents = []
    
    log.info(f"Saving [{len(registered_agents)}] agent(s) to the database.")
    with session_pool() as session:
        repo = agent_domain.RegisteredAgentRepository(session)

        for registered_agent in registered_agents:
            log.info("Converting register agent response to database model")
            try:
                agent_model = agent_domain.RegisteredAgentModel(
                    account_id=registered_agent["data"]["agent"]["accountId"],
                    symbol=registered_agent["data"]["agent"]["symbol"],
                    faction=registered_agent["data"]["agent"]["startingFaction"],
                    headquarters=registered_agent["data"]["agent"]["headquarters"],
                    token=registered_agent["data"]["token"],
                    full_response=registered_agent,
                )
            except Exception as exc:
                msg = f"({type(exc)}) Error converting registered agent to RegisteredAgentModel. Details: {exc}"
                log.error(msg)
                
                continue
            
            log.info("Saving registered agent to database.")
            try:
                registered_agent_model = repo.create(agent_model)
                saved_agents.append(registered_agent_model)
            except Exception as exc:
                msg = f"({type(exc)}) Error creating agent in database. Details: {exc}"
                log.error(msg)
                
                raise exc
            
    log.info(f"Saved [{len(saved_agents)}] agent(s) to the database")


if __name__ == "__main__":
    setup.setup_loguru_logging(
        log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO")
    )
    setup.setup_database(engine=return_engine())
    
    NUM_AGENTS_TO_REGISTER = 5

    log.debug("Test debug message")
    log.debug(f"Database settings: {settings.DB_SETTINGS.as_dict()}")

    demo_register_single_agent()
    demo_register_multiple_agents(num_agents=NUM_AGENTS_TO_REGISTER)
