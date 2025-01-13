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
    
    log.debug("All agents:")
    for agent in all_agents:
        log.debug(f"Agent: {agent.__dict__}")
