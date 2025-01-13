import agent_ctl
import db_lib
import db_lib.demo_db
import depends
from loguru import logger as log
import settings
import setup
from domain.spacetraders import agent as agent_domain


if __name__ == "__main__":
    setup.setup_loguru_logging(
        log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO")
    )
    
    demo_db_engine = db_lib.demo_db.return_demo_engine()
    setup.setup_database(engine=demo_db_engine)
    
    log.debug(f"Database settings: {settings.DB_SETTINGS.as_dict()}")
    
    session_pool = depends.db_depends.get_session_pool(engine=demo_db_engine)
    
    with session_pool() as session:
        repo = agent_domain.RegisteredAgentRepository(session)
        
        all_agents = repo.get_all_agents()
        
    
    log.info(f"Found [{len(all_agents)}] agent(s) in database")
    
    agents: list[agent_domain.RegisteredAgentOut] = []
    conversion_errs: list[agent_domain.RegisteredAgentModel] = []
    
    log.debug("All agents:")
    for agent in all_agents:
        try:
            _agent: agent_domain.RegisteredAgentOut = agent_domain.RegisteredAgentOut.model_validate(agent.__dict__)
            agents.append(_agent)
        except Exception as exc:
            msg = f"({type(exc)}) Error converting agent database model to RegisteredAgentOut schema. Details: {exc}"
            log.error(msg)
            conversion_errs.append(agent)
            
            continue
    
    log.info(f"Converted [{len(agents)}] agent model(s) to RegisteredAgentOut schema(s)")
    if len(conversion_errs) > 0:
        log.warning(f"Errored on [{len(conversion_errs)}] conversion(s) to RegisteredAgentOut.")

    for agent in agents:
        log.info(f"Registered agent: {agent}")
