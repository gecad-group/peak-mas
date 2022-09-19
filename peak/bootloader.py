import importlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import Type

from aioxmpp import JID
from spade import quit_spade

logger = logging.getLogger(__name__)


def boot_agent(
    file: Path,
    jid: JID,
    root_name: str,
    number: int,
    properties: Path,
    log_level: int,
    verify_security: bool,
):
    """Configures logging system and boots the agent.

    Args:
        file: File path where the agent's class is.
        jid: JID of the agent.
        root_name: The root name of the agents that were
            cloned.
        number: If the agent its a clone is the number of present in
            the name of the agent, else its None.
        properties: Properties to be injected in the agent.
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

    _boot_agent(file, jid, root_name, number, properties, verify_security)


def _boot_agent(
    file: Path,
    jid: JID,
    name: str,
    number: int,
    properties: Path,
    verify_security: bool,
):
    """Boots the agent.

    Args:
        file (Path): _description_
        jid (JID): _description_
        name (str): _description_
        number (int): _description_
        properties (Path): _description_
        verify_security (bool): _description_
    """
    # Gets the agent and properties classes. Creates the agent with the 
    # properties and the attributes already provided. Runs the agent and 
    # creates a loop that waits until the agent dies.
    logger.debug("creating agent")
    agent_class = _get_class(file)
    if properties:
        properties = _get_class(properties)(jid.localpart, name, number)
        properties = properties.extract()
    else:
        properties = None

    agent_instance = agent_class(jid, properties, verify_security)
    logger.info("starting agent")
    agent_instance.start().result()
    logger.info("agent running")
    while agent_instance.is_alive():
        try:
            time.sleep(1)
        except Exception as e:
            logger.error("AGENT CRACHED")
            logger.exception(e)
            agent_instance.stop()
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
            agent_instance.stop()
    quit_spade()
    logger.info("agent stoped")


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
