import sys
import typing as t

from project_cli.cli_modules import agent as agent_cli

from cyclopts import App, Group, Parameter
from loguru import logger as log

app = App(name="project_cli", help="CLI for the Spacetraders project.")

app.meta.group_parameters = Group("Session Parameters", sort_key=0)

MOUNT_SUB_CLIS: list = [agent_cli.agent_app]

## Mount apps
for sub_cli in MOUNT_SUB_CLIS:
    app.command(sub_cli)


@app.meta.default
def cli_launcher(*tokens: t.Annotated[str, Parameter(show=False, allow_leading_hyphen=True)], debug: bool = False) :
    """CLI entrypoint."""
    
    if debug:
        log.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | [{level}] | {name}.{function}:{line} |> {message}", level="DEBUG")
        log.debug("CLI debugging enabled")
    else:
        log.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} [{level}]: {message}", level="INFO")
        
    app(tokens)
    

if __name__ == "__main__":
    app()
