import core_utils.hash_utils
import http_lib
import settings
import db_lib
import core_utils

if __name__ == "__main__":
    req = http_lib.build_request(url="https://www.google.com")
    
    try:
        with http_lib.get_http_controller() as http_ctl:
            res = http_ctl.client.send(req)
    except Exception as exc:
        msg = f"({type(exc)}) Error sending request. Details: {exc}"
        raise exc
    
    print(f"Response: [{res.status_code}: {res.reason_phrase}]")
    
    _hash = core_utils.hash_utils.get_hash_from_str(input_str="This is a test!")
    print(f"Hashed string: {_hash}")
