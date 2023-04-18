# Standard library imports
import importlib
import logging
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path
from typing import Type

# Third party imports
from aioxmpp import JID
from spade import quit_spade

logger = logging.getLogger(__name__)


def bootloader(agents: list):
    logger.info("Loading agents")
    procs = []
    for agent in agents:
        proc = Process(target=boot_agent, kwargs=agent, daemon=False)
        proc.start()
        procs.append(proc)
    logger.info("Agents loaded")
    for proc in procs:
        proc.join()


def boot_agent(
    file: Path,
    jid: JID,
    cid: int,
    log_level: int,
    verify_security: bool,
):
    """Configures logging system and boots the agent.

    Args:
        file: File path where the agent's class is.
        jid: JID of the agent.
        name: The name of the agent.
        cid: Clone ID, zero if its the original.
        verify_security: If true it validates the SSL certificates.
    """
    log_file_name: str = jid.localpart + (f"_{jid.resource}" if jid.resource else "")
    logs_folder = file.parent.absolute().joinpath("logs")
    log_file = logs_folder.joinpath(f"{log_file_name}.log")

    os.makedirs(logs_folder, exist_ok=True)
    sys.stdout = open(log_file, "a", buffering=1)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.parent.handlers = []
    logger.parent.addHandler(handler)
    logger.parent.setLevel(log_level)
    handler.setLevel(log_level)

    logger.info("Creating agent from file")
    agent_class = _get_class(file)
    file_abs_path = file.parent.absolute()

    os.chdir(file_abs_path)
    agent_instance = agent_class(jid, cid, verify_security)
    try:
        logger.info("Agent starting")
        agent_instance.start().result()
        logger.info("Agent initialized")
        while agent_instance.is_alive():
            time.sleep(1)
    except Exception as error:
        logger.exception(f"Stoping agent (reason: {error})")
        agent_instance.stop().result()
    except KeyboardInterrupt as error:
        logger.info(f"Stoping agent (reason: {error})")
        agent_instance.stop().result()
    quit_spade()
    logger.info("Agent stoped")


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
