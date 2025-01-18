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
        random_agent: agent_domain.RegisterAgentResponse = agent_domain.convert_agent_dict_to_class(random_agent_dict)
        log.success(f"Converted agent dict to RegisteredAgentResponse object.")
    except Exception as exc:
        msg = f"({type(exc)}) Error converting registered agent response dict to RegisterAgentResponse. Details: {exc}"
        log.error(msg)
        
        raise exc
