# Standard library imports
import importlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import Type

# Third party imports
from aioxmpp import JID
from spade import quit_spade

logger = logging.getLogger(__name__)


def boot_agent(
    file: Path,
    jid: JID,
    name: str,
    number: int,
    log_level: int,
    verify_security: bool,
):
    """Configures logging system and boots the agent.

    Args:
        file: File path where the agent's class is.
        jid: JID of the agent.
        name: The name of the agent.
        number: If the agent its a clone is the number of present in
            the name of the agent, else its None.
        log_level: Logging level to be used in the agents logging file.
        verify_security: If true it validates the SSL certificates.
    """
    log_file_name: str = jid.localpart + ("_" + jid.resource if jid.resource else "")
    logs_folder = file.parent.absolute().joinpath("logs")
    log_file = logs_folder.joinpath(f"{log_file_name}.log")

    os.makedirs(logs_folder, exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        filemode="w",
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    _boot_agent(file, jid, name, number, verify_security)


def _boot_agent(
    file: Path,
    jid: JID,
    name: str,
    number: int,
    verify_security: bool,
):
    """Boots the agent."""
    # Gets the agent and properties classes. Creates the agent with the
    # properties and the attributes already provided. Runs the agent and
    # creates a loop that waits until the agent dies.
    logger.debug("Creating agent.")
    agent_class = _get_class(file)
    file_abs_path = file.parent.absolute()

    os.chdir(file_abs_path)
    agent_instance = agent_class(jid, verify_security)
    logger.debug("Starting agent.")
    try:
        agent_instance.start().result()
        logger.info('Agent initialized.')
        while agent_instance.is_alive():
            time.sleep(1)
    except Exception as error:
        logger.exception(f"Stoping agent (reason: {error}).")
        agent_instance.stop().result()
    except KeyboardInterrupt as error:
        logger.info(f"Stoping agent (reason: {error}).")
        agent_instance.stop().result()
    logger.info("Agent stoped.")
    quit_spade()


def _get_class(file: Path) -> Type:
    """Gets class from a file.

    Reads a python module and retrieves the class with the name of the file.


    Args:
        file: Python module. Must have a class with the same name as the file.
            Example: agent.py --> class agent(...)

    Returns:
        A class object with the same name as the file.
    """
    module_path, module_file = os.path.split(file.absolute())
    module_name = module_file.split(".")[0]
    sys.path.append(module_path)
    module = importlib.import_module(module_name)
    return getattr(module, module_name)
