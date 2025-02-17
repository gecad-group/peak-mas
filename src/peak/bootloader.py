import asyncio
import importlib
import logging
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path
from typing import List, Type
from peak.logging import logger, FORMATTER

from aioxmpp import JID
from spade import quit_spade


async def _wait_for_processes(processes):
    def join_process(process):
        process.join()
        if process.exitcode != 0:
            logger.error(f"{process.name}'s process ended with exitcode {process.exitcode}.")

    await asyncio.gather(
        *[asyncio.to_thread(join_process, process) for process in processes]
    )

def boot_one_agent():
    pass

def boot_several_agents():
    pass

def bootloader(agents: list):
    logger.info(f"creating a process for each of the {len(agents)} agents")
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
    logger.info(f"finished creating the {len(agents)} processes")
    asyncio.run(_wait_for_processes(procs))


def boot_agent(
    file: Path,
    jid: JID,
    cid: int,
    log_level: str,
    verify_security: bool,
    *args,
    **kargs,
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
    log_file = logs_folder.joinpath(f"{log_file_name}.log")
    os.makedirs(logs_folder, exist_ok=True)
    handler = logging.FileHandler(log_file, log_file_mode)
    handler.setFormatter(FORMATTER)
    handler.setLevel(log_level)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.warning('teste')
    logger.addHandler(handler)

    logger.info(f"instanciating agent {jid.localpart} from file {file}")
    agent_class = _get_class(file)
    agent_instance = agent_class(jid, cid, verify_security)

    try:
        logger.info(f"starting agent {jid.localpart}")
        agent_instance.start().result()
        logger.info(f"agent {jid.localpart} started")
        while agent_instance.is_alive():
            time.sleep(1)
    except Exception as error:
        logger.exception(f"stoping agent {jid.localpart} (reason: {error.__class__.__name__})")
        agent_instance.stop().result()
        raise SystemExit(1)
    except KeyboardInterrupt:
        logger.info(f"stoping agent {jid.localpart} (reason: KeyboardInterrupt)")
        agent_instance.stop().result()
    finally:
        quit_spade()
        logger.info(f"agent {jid.localpart} stoped")


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
