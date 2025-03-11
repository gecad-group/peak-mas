import asyncio
import importlib
import logging
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path
from typing import List, Type
import spade
from peak import configure_agent_root_logger, configure_single_agent_logging

from aioxmpp import JID

_logger = logging.getLogger(__name__)


def bootloader(agents: list[dict]):
    if len(agents) == 1:
        boot_single_agent(agents[0])
    else:
        boot_several_agents(agents)

def boot_single_agent(agent: dict):
    _logger.info(f"booting single agent: {agent['jid']}")
    configure_single_agent_logging()
    boot_agent(**agent)

def boot_several_agents(agents: list[dict]):
    _logger.info(f"creating a process for each of the {len(agents)} agents")
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
    _logger.info(f"all {len(agents)} processes created")
    asyncio.run(_wait_for_processes(procs))

def boot_agent(
    file: Path,
    jid: JID,
    cid: int,
    log_level: str,
    logs_folder: Path,
    log_file_mode: str,
    verify_security: bool,
    debug_mode: bool,
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
    agent_logger = configure_agent_root_logger(log_level, log_file, log_file_mode)
    agent_logger.info(f"instanciating agent {jid.localpart} from file {file}")
    agent_class = _get_class(file)
    agent_instance = agent_class(jid, cid, verify_security)

    try:
        agent_logger.info(f"starting agent {jid.localpart}")
        spade.run(agent_instance.start())
        agent_logger.info(f"agent {jid.localpart} terminated")
    except Exception as error:
        agent_logger.exception(f"agent {jid.localpart} terminated ({error.__class__.__name__})", stack_info=True)
        raise SystemExit(1)
    except KeyboardInterrupt:
        agent_logger.info(f"agent {jid.localpart} terminated (KeyboardInterrupt)")
        
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

async def _wait_for_processes(processes):
    def join_process(process):
        process.join()
        if process.exitcode != 0:
            _logger.error(f"{process.name}'s process ended with exitcode {process.exitcode}.")

    await asyncio.gather(
        *[asyncio.to_thread(join_process, process) for process in processes]
    )