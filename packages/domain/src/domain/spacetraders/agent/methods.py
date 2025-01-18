from loguru import logger as log

from domain.spacetraders.agent.schemas import (
    RegisteredAgentIn,
    RegisteredAgentOut,
    RegisterAgentResponse,
)
from domain.spacetraders.agent.models import RegisteredAgentModel
from domain.spacetraders.agent.repository import RegisteredAgentRepository


def convert_agent_schema_to_model(agent: RegisterAgentResponse) -> RegisteredAgentModel:
    """Convert a RegisterAgentResponse class object to a RegisteredAgentModel object.
    
    Params:
        agent (RegisterAgentResponse): A class derived from the response of a POST register agent request.
    
    Returns:
        (RegisterAgentModel): A SQLAlchemy table class for the registered agent.
    
    """
    if agent is None:
        raise ValueError("Missing a Spacetraders Agent.")
    if not isinstance(agent, RegisterAgentResponse):
        raise TypeError(
            f"Invalid type for agent: {type(agent)}. Expected a RegisterAgentResponse class."
        )

    log.debug("Convert RegisteredAgentIn to RegisteredAgentModel")
    try:
        agent_model: RegisteredAgentModel = RegisteredAgentModel(
            symbol=agent.symbol,
            faction=agent.faction,
            headquarters=agent.headquarters,
            token=agent.token,
            full_response=agent.response_content,
        )

        return agent_model
    except Exception as exc:
        msg = f"({type(exc)}) Error converting RegisteredAgentIn to RegisteredAgentModel. Details: {exc}"
        log.error(msg)

        raise exc


def convert_agent_model_to_schema() -> RegisteredAgentOut: ...


def convert_agent_dict_to_class(agent_dict: dict) -> RegisterAgentResponse:
    """Convert a dict representing the response from an HTTP POST request to register a new agent."""
    try:
        agent: RegisterAgentResponse = RegisterAgentResponse(response_content=agent_dict)
        log.debug("Converted registered agent response dict to RegisterAgentResponse object.")

        return agent
    except Exception as exc:
        msg = f"({type(exc)}) Error converting registered agent response dict to RegisterAgentResponse. Details: {exc}"
        log.error(msg)
        
        raise exc