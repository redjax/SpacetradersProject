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
    demo_db_engine = db_lib.demo_db.return_demo_engine()
    setup.setup_database(engine=demo_db_engine)
    
    random_agent_dict = agent_ctl.register_random_agent(retry_on_taken_username=True)
    log.debug(f"Random agent: {random_agent_dict}")
    
    log.info("Converting registered agent response dict to RegisterAgentResponse")
    try:
        random_agent: agent_domain.RegisterAgentResponse = agent_ctl.convert_agent_dict_to_class(random_agent_dict)
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


    # log.info(f"Converting agent dict to database model")
    # try:
    #     random_agent_model = agent_ctl.convert_agent_schema_to_model(agent=random_agent)
    # except Exception as exc:
    #     msg = f"({type(exc)}) Error converting registered agent response to database model."
    #     log.error(msg)
        
    #     raise exc
    
    # log.debug(f"RegisteredAgentModel: {random_agent_model.__dict__}")
    
    # log.info("Saving registered agent model to database.")
    # try:
    #     agent_ctl.db_client.save_registered_agent_to_db(agent=)
    # except Exception as exc:
    #     log.error(f"({type(exc)}) Error saving registered agent to database. Details: {exc}")
        
    #     raise exc
