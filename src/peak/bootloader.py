import asyncio
import importlib
import logging
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path
from typing import List, Type

from aioxmpp import JID
from spade import quit_spade

logger = logging.getLogger(__name__)


async def _wait_for_processes(processes):
    def join_process(process):
        process.join()
        if process.exitcode != 0:
            logger.error(f"{process.name}'s process ended unexpectedly.")

    await asyncio.gather(
        *[asyncio.to_thread(join_process, process) for process in processes]
    )


def bootloader(agents: list):
    logger.info("Loading agents")
    procs: List[Process] = []
    for i, agent in enumerate(agents):
        proc = Process(
            target=boot_agent,
            kwargs=agent,
            daemon=False,
            name=agents[i]["jid"].localpart,
        )
        proc.start()
        procs.append(proc)
    logger.info("Agents loaded")
    asyncio.run(_wait_for_processes(procs))


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
    sys.stderr = sys.stdout
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
    os.chdir(file.parent.absolute())
    agent_instance = agent_class(jid, cid, verify_security)

    try:
        logger.info("Agent starting")
        agent_instance.start().result()
        logger.info("Agent initialized")
        while agent_instance.is_alive():
            time.sleep(1)
    except Exception as error:
        logger.exception(f"Stoping agent (reason: {error.__class__.__name__})")
        agent_instance.stop().result()
        raise SystemExit(1)
    except KeyboardInterrupt:
        logger.info(f"Stoping agent (reason: KeyboardInterrupt)")
        agent_instance.stop().result()
    finally:
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
    try:
        module_path, module_file = os.path.split(file.absolute())
        module_name = module_file.split(".")[0]
        sys.path.append(module_path)
        module = importlib.import_module(module_name)
        return getattr(module, module_name)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            f"the file does not exist or the file name wasn't used as the agent's class name ({file})"
        )
