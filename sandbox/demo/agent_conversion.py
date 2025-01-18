import db_lib.demo_db
from loguru import logger as log

import db_lib
from depends import db_depends
import setup
import settings
import agent_ctl
from domain.spacetraders import agent as agent_domain

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))
    db_config = db_lib.demo_db.DEMO_DB_CONFIG
    log.debug(f"DB config: {db_config}")
    demo_db_engine = db_lib.demo_db.return_demo_engine(db_conf=db_config)
    setup.setup_database(engine=demo_db_engine)
    
    random_agent_dict = agent_ctl.register_random_agent(retry_on_taken_username=True)
    log.debug(f"Random agent: {random_agent_dict}")
    
    log.info("Converting registered agent response dict to RegisterAgentResponse")
    try:
        random_agent: agent_domain.RegisterAgentResponse = agent_ctl.convert_register_agent_res_dict_to_class(random_agent_dict)
        log.success(f"Converted agent dict to RegisteredAgentResponse object.")
    except Exception as exc:
        msg = f"({type(exc)}) Error converting registered agent response dict to RegisterAgentResponse. Details: {exc}"
        log.error(msg)
        
        raise exc
    log.debug(f"RegisterAgentResponse: {random_agent}")
    
    log.info("Converting RegisterAgentResponse to RegisteredAgentIn schema")
    try:
        random_agent_schema = agent_ctl.convert_http_response_schema_to_agent_in_schema(registered_agent=random_agent)
        log.success(f"Converted RegisterAgentResponse class to RegisteredAgentIn class.")
        log.debug(f"RegisteredAgentIn: {random_agent_schema}")
    except Exception as exc:
        msg = f"({type(exc)}) Error converting RegisterAgentSchema to RegisteredAgentIn. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    log.info("Saving registered agent model to database.")
    try:
        db_agent = agent_ctl.db_client.save_registered_agent_to_db(agent=random_agent_schema, engine=demo_db_engine)
        log.success(f"Saved agent {db_agent.symbol} successfully.")
        log.debug(f"Agent database entity: {db_agent.__dict__}")
    except Exception as exc:
        log.error(f"({type(exc)}) Error saving registered agent to database. Details: {exc}")
        
        raise exc
    
    log.info("Converting registered agent from database to RegisteredAgentOut")
    db_agent_schema: agent_domain.RegisteredAgentOut = agent_ctl.convert_agent_model_to_schema(db_agent=db_agent)
    log.info(f"Agent from database: {db_agent_schema}")
