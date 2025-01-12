import core_utils.hash_utils
import http_lib
import settings
import db_lib
import core_utils
import setup

from loguru import logger as log

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))
    
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
