from __future__ import annotations

import json

from agent_ctl.constants import API_AGENT_REGISTER_URL
from domain.spacetraders import agent as agent_domain
import http_lib
import httpx
from loguru import logger as log

def build_register_agent_request(
    agent_symbol: str = None,
    agent_faction: str = "COSMIC",
    headers: dict = {"Content-Type": "application/json"},
) -> httpx.Request:
    assert agent_symbol is not None, ValueError("agent_symbol cannot be None")
    assert isinstance(agent_symbol, str), TypeError(
        f"agent_symbol should be of type str. Got type: ({type(agent_symbol)})"
    )
    assert agent_faction is not None, ValueError("agent_faction cannot be None")
    assert isinstance(agent_faction, str), TypeError(
        f"agent_faction should be of type str. Got type: ({type(agent_faction)})"
    )
    assert headers is not None, ValueError("headers object should cannot be None")
    assert isinstance(headers, dict), TypeError(
        f"headers should be of type dict. Got type: ({type(headers)})"
    )

    json_body: dict = {"symbol": agent_symbol, "faction": agent_faction}

    request: httpx.Request = httpx.Request(
        method="POST", url=API_AGENT_REGISTER_URL, json=json_body, headers=headers
    )

    return request


def send_register_agent_request(request_obj: httpx.Request = None, use_cache: bool = False) -> httpx.Response:
    if not request_obj:
        raise ValueError("request_obj cannot be None")
    if not isinstance(request_obj, httpx.Request):
        raise TypeError(
        f"request_obj must be of type httpx.Request. Got type: ({type(request_obj)})"
    )

    log.debug(f"Registering agent with Spacetraders API, request URL: {request_obj.url}")
    with http_lib.get_http_controller(use_cache=use_cache) as http_ctl:
    # with httpx.Client() as client:
        try:
            res: httpx.Response = http_ctl.client.send(request_obj)
            log.debug(f"Register agent res: [{res.status_code}: {res.reason_phrase}]")

            return res
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception sending register agent request. Details: {exc}"
            )
            log.error(msg)

            raise msg


def parse_register_agent_response(response_obj: httpx.Response = None) -> dict:
    try:
        content_decode: str = response_obj.content.decode("utf-8")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception decoding response content. Details: {exc}"
        )
        log.error(msg)

        raise msg

    try:
        _json: dict = json.loads(content_decode)

        return _json
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading JSON content from decoded content string. Details: {exc}"
        )
        log.error(msg)

        raise msg


def register_agent(agent_symbol: str = None, agent_faction: str = "COSMIC", headers: dict = { "Content-Type": "application/json" }, use_cache: bool = False) -> dict:
    try:
        register_req = build_register_agent_request(agent_symbol=agent_symbol, agent_faction=agent_faction, headers=headers)
    except Exception as exc:
        msg = f"({type(exc)}) Error building register agent request. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    try:
        register_agent_res = send_register_agent_request(request_obj=register_req, use_cache=use_cache)
    except Exception as exc:
        msg = f"({type(exc)}) Error sending register agent request. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    if register_agent_res.status_code == 409:
        raise agent_domain.exc.AgentAlreadyRegisteredException(symbol=agent_symbol)
    
    try:
        parsed_agent = parse_register_agent_response(response_obj=register_agent_res)
        
        return parsed_agent
    except Exception as exc:
        msg = f"({type(exc)}) Error parsing register agent response to dict. Details: {exc}"
        log.error(msg)
        
        raise exc


def register_multiple_agents(agents: list[dict], headers: dict = { "Content-Type": "application/json" }, use_cache: bool = False) -> list[dict]:
    # agent_symbol: str = None, agent_faction: str = "COSMIC",
    log.debug(f"Registering [{len(agents)}] agent(s)")
    
    agent_responses: list[dict] = []
    
    for agent in agents:
        agent_symbol: str = agent["symbol"]
        agent_faction: str = agent["faction"]
        
        try:
            registered_agent_dict: dict = register_agent(agent_symbol=agent_symbol, agent_faction=agent_faction, headers=headers)
            agent_responses.append(registered_agent_dict)
        except Exception as exc:
            msg = f"({type(exc)}) Error registering agent '{agent_symbol}'. Details: {exc}"
            log.error(msg)
            
            continue
    
    log.debug(f"Successfully registered [{len(agent_responses)}] agent(s).")
    
    return agent_responses
