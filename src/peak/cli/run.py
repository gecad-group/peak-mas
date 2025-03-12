import io
import logging
import sys
from argparse import ArgumentTypeError
from pathlib import Path

import yaml

from peak import JID
from peak.bootloader import bootloader

_logger = logging.getLogger(__name__)


def execute_agent(
    file: Path,
    jid: JID,
    clones: int,
    log_level: str,
    log_file: io.TextIOWrapper,  # stream type
    # log_file_mode: str,
    verify_security: bool = False,
    *args,
    **kargs,
):
    """Executes a single agent.

    Args:
        file: Path to the agent's python file.
        jid: JID of the agent.
        clones: Number of clones to be made.
        log_level: Logging level.
        verify_security: Verifies the SSL certificates.
    """
    # TODO: verify at argsparser level
    if file and not file.is_file():
        raise ArgumentTypeError(f"Agent's file must be a python file, not '{file}'.")

    kwargs = {
        "file": file,
        "jid": jid,
        "cid": 0,
        "log_level": log_level,
        "log_file": log_file if clones == 0 else file.parent,
        "verify_security": verify_security,
    }

    name = jid.localpart
    agents = []
    for cid in range(clones):
        agent = kwargs.copy()
        agents.append(agent)
        kwargs["jid"] = kwargs["jid"].replace(localpart=f"{name}{cid}")
        kwargs["cid"] = cid
    bootloader(agents)


def execute_config_file(file: Path, *args, **kargs):
    """Executes agents using a YAML configuration file.

    Args:
        file: Path to the agent's python file.
    """

    _logger.info("parsing YAML configuration file")
    defaults = {
        "file": None,
        "domain": "localhost",
        "resource": "main",
        "ssl": False,
        "log_level": "info",
        "log_folder": file.parent.joinpath("logs"),
        "log_file_mode": "a",
        "debug_mode": False,
        "clones": 1,
    }
    agents = []

    with file.open() as f:
        yml = yaml.full_load(f)
    sys.path.append(
        str(file.parent.absolute())
    )  # imports any python modules in the parent folder of the yaml file

    if "defaults" in yml:
        defaults = defaults | yml["defaults"]
    if "agents" not in yml:
        raise Exception("YAML: 'agents' argument required")
    for agent_name, agent_args in yml["agents"].items():
        if agent_args is not None:
            agent_args = defaults | agent_args
        else:
            agent_args = defaults
        if agent_args["file"] is None:
            raise Exception(f"{agent_name}: file argument required")
        if agent_args["domain"] is None:
            raise Exception(f"{agent_name}: domain argument required")
        kwargs = {
            "file": Path(agent_args["file"]),
            "jid": JID(agent_name, agent_args["domain"], agent_args["resource"]),
            "cid": 0,
            "log_level": agent_args["log_level"].upper(),
            "log_folder": file.parent.joinpath(agent_args["log_folder"]),
            "log_file_mode": agent_args["log_file_mode"],
            "verify_security": agent_args["ssl"],
            "debug_mode": agent_args["debug_mode"],
        }
        if agent_args["clones"] > 1:
            for cid in range(agent_args["clones"]):
                kwargs["jid"] = kwargs["jid"].replace(localpart=f"{agent_name}{cid}")
                kwargs["cid"] = cid
                agent = kwargs.copy()
                agents.append(agent)
        else:
            agents.append(kwargs)

    _logger.info("YAML configuration file parsed")
    bootloader(agents)
