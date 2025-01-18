import db_lib.demo_db
from loguru import logger as log

import db_lib
from depends import db_depends
from domain.spacetraders import agent as agent_domain
import agent_ctl
from pipelines.spacetraders_api_pipelines import agent_pipelines
import setup
import settings


def main(db_engine=None, num_agents_to_register: int = 3):
    log.info("Starting agent registration pipeline")
    
    registered_agent_models: list[agent_domain.RegisteredAgentModel] | None = agent_pipelines.pipeline_register_random_agents(num_agents=num_agents_to_register, save_to_db=True, db_engine=db_engine)
    if registered_agent_models:
        log.info(f"Registered [{len(registered_agent_models)}] agent(s). List is RegisteredAgentModel objects")
    
    registered_agent_model_schemas: list[agent_domain.RegisteredAgentOut]  | None= agent_pipelines.pipeline_register_random_agents(num_agents=num_agents_to_register, save_to_db=True, db_engine=db_engine, return_schemas=True)
    if registered_agent_model_schemas:
        log.info(f"Registered [{len(registered_agent_model_schemas)}] agent(s). List is RegisteredAgentOut objects")
        
    log.info(f"Registered [{len(registered_agent_models) + len(registered_agent_model_schemas)}] agent(s) in total.")
    

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    demo_db_config = db_lib.demo_db.return_demo_db_config()
    demo_db_engine = db_lib.demo_db.return_demo_engine(db_conf=demo_db_config)
    
    setup.setup_database(engine=demo_db_engine)
    
    main(db_engine=demo_db_engine, num_agents_to_register=3)