from __future__ import annotations

import agent_ctl
import core_utils
import core_utils.hash_utils
import core_utils.uuid_utils
import db_lib
import http_lib
from loguru import logger as log
import settings
import setup
from domain.spacetraders import agent as agent_domain

demo_db_dict = {
    "drivername": "sqlite+pysqlite",
    "username": None,
    "password": None,
    "host": None,
    "port": None,
    "database": ".db/demo.sqlite3",
}


def return_engine(db_conf: dict = demo_db_dict, echo: bool = False):
    db_uri = db_lib.get_db_uri(**db_conf)
    engine = db_lib.get_engine(url=db_uri, echo=echo)

    return engine


if __name__ == "__main__":
    print(f"Database settings: {settings.DB_SETTINGS.as_dict()}")
    setup.setup_loguru_logging(
        log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO")
    )
    setup.setup_database(engine=return_engine())

    log.debug("Test debug message")

    req = http_lib.build_request(url="https://www.google.com")

    try:
        with http_lib.get_http_controller() as http_ctl:
            res = http_ctl.client.send(req)
    except Exception as exc:
        msg = f"({type(exc)}) Error sending request. Details: {exc}"
        raise exc

    log.info(f"Response: [{res.status_code}: {res.reason_phrase}]")

    _hash = core_utils.hash_utils.get_hash_from_str(input_str="This is a test!")
    log.info(f"Hashed string: {_hash}")

    log.info("Testing register agent")
    try:
        register_agent_response = agent_ctl.register_agent(
            agent_symbol=core_utils.uuid_utils.get_rand_uuid(
                characters=14, as_str=True
            ),
            use_cache=True,
        )
    except Exception as exc:
        msg = f"({type(exc)}) Error registering demo agent. Details: {exc}"
        log.error(msg)

        raise exc

    log.info(f"Registered agent: {register_agent_response}")

    session_pool = db_lib.get_session_pool(engine=return_engine())
    with session_pool() as session:
        repo = agent_domain.RegisteredAgentRepository(session)

        log.info("Converting register agent response to database model")
        try:
            agent_model = agent_domain.RegisteredAgentModel(
                account_id=register_agent_response["data"]["agent"]["accountId"],
                symbol=register_agent_response["data"]["agent"]["symbol"],
                faction=register_agent_response["data"]["agent"]["startingFaction"],
                headquarters=register_agent_response["data"]["agent"]["headquarters"],
                token=register_agent_response["data"]["token"],
                full_response=register_agent_response,
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error converting registered agent to RegisteredAgentModel. Details: {exc}"
            log.error(msg)
            
            raise exc
        
        log.info("Saving registered agent to database.")
        try:
            repo.create(agent_model)
        except Exception as exc:
            msg = f"({type(exc)}) Error creating agent in database. Details: {exc}"
            log.error(msg)
            
            raise exc
