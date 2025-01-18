from loguru import logger as log

import typing as t
from domain.spacetraders.agent.schemas import (
    RegisteredAgentIn,
    RegisteredAgentOut,
    RegisterAgentResponse,
)
from domain.spacetraders.agent.models import RegisteredAgentModel
from domain.spacetraders.agent.repository import RegisteredAgentRepository


def convert_agent_schema_to_model(agent: t.Union[RegisterAgentResponse, RegisteredAgentIn]) -> RegisteredAgentModel:
    """Convert a RegisterAgentResponse class object to a RegisteredAgentModel object.
    
    Params:
        agent (RegisterAgentResponse): A class derived from the response of a POST register agent request.
    
    Returns:
        (RegisterAgentModel): A SQLAlchemy table class for the registered agent.
    
    """
    if agent is None:
        raise ValueError("Missing a Spacetraders Agent.")
    if not isinstance(agent, RegisterAgentResponse) and not isinstance(agent, RegisteredAgentIn):
        raise TypeError(
            f"Invalid type for agent: {type(agent)}. Expected a RegisterAgentResponse or RegisteredAgentIn class."
        )

    log.debug("Convert RegisteredAgentIn to RegisteredAgentModel")
    try:
        agent_model: RegisteredAgentModel = RegisteredAgentModel(
            account_id=agent.account_id,
            symbol=agent.symbol,
            faction=agent.faction,
            headquarters=agent.headquarters,
            token=agent.token,
            full_response=agent.full_response,
        )

        return agent_model
    except Exception as exc:
        msg = f"({type(exc)}) Error converting RegisteredAgentIn to RegisteredAgentModel. Details: {exc}"
        log.error(msg)

        raise exc


def convert_agent_model_to_schema(db_agent: RegisteredAgentModel) -> RegisteredAgentOut:
    """Convert RegisteredAgentModel database entity to RegisteredAgentOut schema.
    
    Params:
        db_agent (RegisteredAgentModel): Database entity representing a registered agent.
        
    Returns:
        (RegisteredAgentOut): Schema object representing a registered agent in the database.
    
    """
    log.debug("Converting registered agent database entity to schema.")
    try:
        converted_agent: RegisteredAgentOut = RegisteredAgentOut.model_validate(db_agent.__dict__)
        log.debug("Converted registered agent database entity to RegisteredAgentOut schema.")
        
        return converted_agent
    except Exception as exc:
        msg = f"({type(exc)}) Error converting registered agent database entity to RegisteredAgentOut. Details: {exc}"
        log.error(msg)
        
        raise exc


def convert_register_agent_res_dict_to_class(agent_dict: dict) -> RegisterAgentResponse:
    """Convert a dict representing the response from an HTTP POST request to register a new agent."""
    try:
        agent: RegisterAgentResponse = RegisterAgentResponse(full_response=agent_dict)
        log.debug("Converted registered agent response dict to RegisterAgentResponse object.")

        return agent
    except Exception as exc:
        msg = f"({type(exc)}) Error converting registered agent response dict to RegisterAgentResponse. Details: {exc}"
        log.error(msg)
        
        raise exc
    

def convert_http_response_schema_to_agent_in_schema(registered_agent: RegisterAgentResponse) -> RegisteredAgentIn:
    """Convert a RegisterAgentResponse (schema derived from HTTP response object from POST /register) to a RegisteredAgentIn schema.
    
    Params:
        registered_agent (RegisterAgentResponse): A schema class derived from a successful HTTP POST request to /register. This is a more
            'raw' version of the schema, where the output is structured specifically for internal use in the application.
    
    Returns:
        (RegisteredAgentIn): A converted schema class.

    """
    if not registered_agent:
        raise ValueError("Missing a RegisterAgentResponse input object.")
    
    if not isinstance(registered_agent, RegisterAgentResponse):
        raise TypeError(f"Invalid type for registered_agent: ({type(registered_agent)}). Must be of type RegisterAgentResponse.")
    
    log.debug("Converting RegisterAgentResponse schema to RegisteredAgentIn schema.")
    try:
        registered_agent_dict: dict = registered_agent.model_dump()
        converted_agent: RegisterAgentResponse = RegisteredAgentIn.model_validate(registered_agent_dict)
        log.debug("Successfully converted RegisterAgentResponse object to RegisteredAgentIn")
        
        return converted_agent
    except Exception as exc:
        log.error(f"Error converting RegisterAgentResponse object to RegisteredAgentIn schema. Details: {exc}")
        raise exc
