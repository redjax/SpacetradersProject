from __future__ import annotations

import time
import agent_ctl
import db_lib
import db_lib.demo_db
from depends import db_depends
from domain.spacetraders import agent as agent_domain
from loguru import logger as log
from pipelines.spacetraders_api_pipelines import agent_pipelines
import settings
import setup
import sqlalchemy as sa

def demo_register_random_agents(db_engine: sa.Engine, num_agents_to_register: int  = 4):
    registered_agent_models: list[agent_domain.RegisteredAgentModel] | None = agent_pipelines.pipeline_register_random_agents(num_agents=num_agents_to_register, save_to_db=True, db_engine=db_engine)
    log.debug(f"registered_agent_models type: ({type(registered_agent_models)})")
    log.debug(f"List is empty: {registered_agent_models is None}")
    if registered_agent_models:
        log.info(f"Registered [{len(registered_agent_models)}] agent(s). List is RegisteredAgentModel objects")

    return registered_agent_models

def demo_register_random_agents_return_schemas(db_engine: sa.Engine, num_agents_to_register: int  = 4):
    registered_agent_model_schemas: list[agent_domain.RegisteredAgentOut]  | None= agent_pipelines.pipeline_register_random_agents(num_agents=num_agents_to_register, save_to_db=True, db_engine=db_engine, return_schemas=True)
    log.debug(f"registered_agent_model_schemas type: ({type(registered_agent_model_schemas)})")
    if registered_agent_model_schemas:
        log.info(f"Registered [{len(registered_agent_model_schemas)}] agent(s). List is RegisteredAgentOut objects")


def main(db_engine=None, num_agents_to_register: int = 3):
    log.info("Starting agent registration pipeline")
    
    # registered_agent_models = demo_register_random_agents(db_engine=db_engine, num_agents_to_register=num_agents_to_register)
    # log.debug(f"Registered agent models ({type(registered_agent_models)}), list is empty: {registered_agent_models is None}")
    # if registered_agent_models is not None:
    #     log.info(f"Returned [{len(registered_agent_models)}] registered agent models.")
    #     for _agent_model in registered_agent_models:
    #         print(f"Agent ({type(_agent_model)}): {_agent_model}")
    
    # log.info("\nShort sleep after registering agents, before registering a new batch and returning schemas\n")
    # time.sleep(2)

    registered_agent_model_schemas = demo_register_random_agents_return_schemas(db_engine=db_engine, num_agents_to_register=num_agents_to_register)
    log.debug(f"Registered agent schemas ({type(registered_agent_model_schemas)}), list is empty: {registered_agent_model_schemas is None}")
    if registered_agent_model_schemas is not None:
        log.info(f"Returned [{len(registered_agent_model_schemas)}] registered agent schemas.")
        for _agent_schema in registered_agent_model_schemas:
            print(f"Agent schema ({type(_agent_schema)}): {_agent_schema}")
    

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    demo_db_config = db_lib.demo_db.return_demo_db_config(database=settings.DB_SETTINGS.get("DB_DATABASE", default=".db/demo.sqlitee3"))
    demo_db_engine = db_lib.demo_db.return_demo_engine(db_conf=demo_db_config)
    
    setup.setup_database(engine=demo_db_engine)
    
    main(db_engine=demo_db_engine, num_agents_to_register=2)