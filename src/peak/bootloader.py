import asyncio
import importlib
import logging
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path
from typing import List, Type

from aioxmpp import JID, node

from peak import (
    configure_debug_mode,
    configure_multiple_agent_logging,
    configure_single_agent_logging,
)

_logger = logging.getLogger(__name__)


def bootloader(agents: list[dict]):
    if len(agents) == 1:
        boot_single_agent(agents[0])
    else:
        boot_several_agents(agents)


def boot_single_agent(agent: dict):
    _logger.info(f"booting single agent: {agent['jid']}")
    # configure_single_agent_logging()
    boot_agent(**agent, single_agent=True)


def boot_several_agents(agents: list[dict]):
    _logger.info(f"booting {len(agents)} agents (multiprocess)")
    # configure_multiple_agent_logging()
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
    log_folder: Path,
    log_file_mode: str,
    verify_security: bool,
    debug_mode: bool,
    port: int,
    single_agent: bool = False,
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
    try:
        log_file_name: str = jid.localpart + (
            f"_{jid.resource}" if jid.resource else ""
        )
        log_file = log_folder.joinpath(f"{log_file_name}.log")
        os.makedirs(log_folder, exist_ok=True)
        if single_agent:
            configure_single_agent_logging(log_level, log_file, log_file_mode)
        else:
            configure_multiple_agent_logging(log_level, log_file, log_file_mode)
        if debug_mode:
            configure_debug_mode(log_level, log_file, log_file_mode)
        _logger.info(f"instanciating agent {jid.localpart} from file {file}")
        # add port to aioxmpp
        node.discover_connectors = _change_discover_connectors_port(
            node.discover_connectors, port
        )
        agent_class = _get_class(file)
        agent_instance = agent_class(jid, cid, verify_security)
        _logger.info(f"starting agent {jid.localpart}")
        agent_instance.start().result()
        while agent_instance.is_alive():
            time.sleep(1)
        _logger.info(f"agent {jid.localpart} terminated")
    # except Exception as error:
    #    _logger.critical(f"agent {jid.localpart} terminated ({error.__class__.__name__}: {error})", exc_info=True)
    #    raise SystemExit(1)
    except KeyboardInterrupt:
        _logger.info(f"agent {jid.localpart} terminated (KeyboardInterrupt)")


def _get_class(file: Path) -> Type:
    """Gets class from a file.

    Reads a python module and retrieves the class with the name of the file.


    Args:
        file: Python module. Must have a class with the same name as the file.
            Example: agent123.py --> class agent123(...)

    Returns:
        A class object with the same name as the file.
    """
    if not file.is_file():
        raise FileNotFoundError(
            f"cannot instatiate agent from a non-existing file ({file})"
        )
    module_path, module_file = os.path.split(file.absolute())
    module_name = module_file.split(".")[0]
    sys.path.append(module_path)
    module = importlib.import_module(module_name)
    return getattr(module, module_name)


async def _wait_for_processes(processes):
    def join_process(process):
        process.join()
        if process.exitcode != 0:
            _logger.error(
                f"{process.name}'s process ended with exitcode {process.exitcode}."
            )

    await asyncio.gather(
        *[asyncio.to_thread(join_process, process) for process in processes]
    )


def _change_discover_connectors_port(original_function, new_port):
    async def new_function(*args, **kwargs):
        server_list = await original_function(*args, **kwargs)
        new_server_list = []
        for domain, _, connector in server_list:
            new_server_list.append(
                (domain, new_port, connector)  # Change the port to the new one
            )
        return new_server_list

    return new_function
