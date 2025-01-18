from __future__ import annotations

from project_cli.main import app as cli_app

from cyclopts import App
from loguru import logger as log

def start_cli(app: App = cli_app):
    try:
        app.meta()
    except Exception as exc:
        msg = f"({type(exc)}) Error running CLI. Details: {exc}"
        log.error(msg)
        
        raise exc
    
    
if __name__ == "__main__":
    start_cli(app=cli_app)
