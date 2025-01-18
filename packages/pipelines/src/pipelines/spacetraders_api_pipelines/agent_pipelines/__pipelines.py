from __future__ import annotations

import time
import typing as t
import json

import agent_ctl
import db_lib
from depends import db_depends
from domain.spacetraders import agent as agent_domain
from loguru import logger as log
import settings
import sqlalchemy as sa

def pipeline_register_random_agents(num_agents: int = 3, loop_sleep: int = 5, save_to_db: bool = False, db_engine: sa.Engine | None = None, return_schemas: bool = False) -> list[t.Union[agent_domain.RegisteredAgentModel, agent_domain.RegisteredAgentIn, agent_domain.RegisteredAgentOut]]:
    if save_to_db:
        if not db_engine:
            log.warning("save_to_db=True but missing database engine. Initializing one from app's configuration")
            try:
                db_engine: sa.Engine = db_depends.get_db_engine()
            except Exception as exc:
                msg = f"({type(exc)}) Error initializing database engine. Details: {exc}"
                log.error(msg)
                
                raise exc

    loop: int = 0
    
    errors: list[str] = []
    registered_agents: list[dict] = []
    unavailable_symbols: list[str] = []
    
    if num_agents > 1:
        log.info(f"Registering {num_agents} random agents")
        while loop < num_agents:
            rand_symbol: str = agent_ctl.get_random_agent_symbol()
            log.debug(f"[agent #{loop + 1}] Register agent '{rand_symbol}'")
            
            try:
                rand_agent: dict = agent_ctl.register_agent(agent_symbol=rand_symbol)
                registered_agents.append(rand_agent)
            except agent_domain.exc.AgentAlreadyRegisteredException:
                log.warning(f"Agent '{rand_symbol}' already registered. Generating new name & retrying.")
                continue
            except Exception as exc:
                msg = f"({type(exc)}) Error registering agent. Details: {exc}"
                log.error(msg)
                
                errors.append(rand_symbol)

            loop += 1
            
            if loop_sleep and loop_sleep > 0 and loop < num_agents:
                log.info(f"[{loop}/{num_agents}] Sleeping for [{loop_sleep}] second(s) between requests...")
                time.sleep(loop_sleep)

        log.info(f"Registered [{len(registered_agents)}] agent(s). Encountered [{len(unavailable_symbols)}] taken/registered symbol(s). Errored on [{len(errors)}] request(s)")

    else:
        log.info("Registering single random agent")
        rand_symbol: str = agent_ctl.get_random_agent_symbol()
        log.debug(f"Registering agent '{rand_symbol}'")
        
        RETRY: bool = True
        
        while RETRY:
            try:
                rand_agent: dict = agent_ctl.register_agent(agent_symbol=rand_symbol)
                RETRY=False
                
                ## Add single agent to registered agent list
                registered_agents.append(rand_agent)
            except agent_domain.exc.AgentAlreadyRegisteredException:
                log.warning(f"Symbol '{rand_symbol}' is already registered. Retrying with new symbol.")
                unavailable_symbols.append(rand_symbol)
                
                continue
            except Exception as exc:
                msg = f"({type(exc)}) Error registering agent '{rand_symbol}'. Details: {exc}"
                log.error(msg)
                
                raise exc
            
        log.success(f"Registered agent '{rand_symbol}'.")
        
    register_agent_http_res_schemas: list[agent_domain.RegisteredAgentIn] = []
    convert_http_res_to_schema_errors: list[dict] = []
        
    log.info(f"Converting [{len(registered_agents)}] agent dict(s) to schemas")
    for agent_dict in registered_agents:
        try:
            agent_dict_to_http_res_schema: agent_domain.RegisterAgentResponse = agent_ctl.convert_register_agent_res_dict_to_class(agent_dict=agent_dict)
            registered_agent_schema: agent_domain.RegisteredAgentIn = agent_ctl.convert_http_response_schema_to_agent_in_schema(registered_agent=agent_dict_to_http_res_schema)
            log.info("Converted registered agent HTTP response object to RegisteredAgentIn schema.")
            register_agent_http_res_schemas.append(registered_agent_schema)
            continue
        except Exception as exc:
            msg = f"({type(exc)}) Error converting agent dict to RegisteredAgentIn schema. Details: {exc}"
            log.error(msg)
            
            convert_http_res_to_schema_errors.append(agent_dict)
            continue
    
    log.info(f"Converted [{len(register_agent_http_res_schemas)}] registered agent HTTP response(s) to RegisteredAgentIn schemas. Error on [{len(convert_http_res_to_schema_errors)}] conversion(s)")
    
    if not save_to_db:
        log.debug("save_to_db=False, return list of RegisteredAgentIn object(s)")
        return register_agent_http_res_schemas
    
    log.info(f"Saving [{len(registered_agents)}] agent(s) to database")
    agents_saved_to_db = agent_ctl.db_client.save_multiple_registered_agents_to_db(agents=register_agent_http_res_schemas, engine=db_engine)

    log.info(f"Saved [{len(agents_saved_to_db)}] agent(s) to database.")

    if return_schemas:
        log.debug("return_schemas=True, converting RegisteredAgentModel object to RegisteredAgentOut object.")

        agent_schemas: list[agent_domain.RegisteredAgentOut] = []
        errored_converting_model_to_schema: list[agent_domain.RegisteredAgentModel] = []
        
        for db_agent in agents_saved_to_db:
            log.debug(f"Converting agent ({type(db_agent)}): {db_agent}")
            try:
                converted_agent: agent_domain.RegisteredAgentOut = agent_ctl.convert_agent_model_to_schema(db_agent=db_agent)
                agent_schemas.append(converted_agent)
                
                continue
            except Exception as exc:
                log.error(f"Errored converting agent '{db_agent.symbol}' to RegisteredAgentOut object. Details: {exc}")
                errored_converting_model_to_schema.append(db_agent)
                
                continue
            
        if errored_converting_model_to_schema:
            log.warning(f"Saved [{len(agents_saved_to_db)}], errored converting [{len(errored_converting_model_to_schema)}] database model(s) to RegisteredAgentOut schema(s). Returning [{len(agent_schemas)}] agent schema(s)")
            
        return agent_schemas
    else:
        return agents_saved_to_db
