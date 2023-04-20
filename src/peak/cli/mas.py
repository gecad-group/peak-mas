from argparse import ArgumentTypeError
from logging import getLevelName, getLogger
from os import chdir
from pathlib import Path

import yaml

from peak import JID
from peak.bootloader import bootloader

_logger = getLogger(__name__)


def agent_exec(
    file: Path,
    jid: JID,
    clones: int = 1,
    log_level: int = getLevelName("INFO"),
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


def multi_agent_exec(file: Path, log_level, *args, **kargs):
    """Executes agents using a YAML configuration file.

    Args:
        file: Path to the agent's python file.
    """

    _logger.info("Parsing YAML file")
    defaults = {
        "file": None,
        "domain": None,
        "resource": None,
        "ssl": False,
        "log_level": log_level,
        "clones": 1,
    }
    agents = []

    with file.open() as f:
        yml = yaml.full_load(f)
    chdir(file.parent)

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
            "log_level": agent_args["log_level"],
            "verify_security": agent_args["ssl"],
        }
        for cid in range(agent_args["clones"]):
            agent = kwargs.copy()
            agents.append(agent)
            kwargs["jid"] = kwargs["jid"].replace(localpart=f"{agent_name}{cid}")
            kwargs["cid"] = cid
    bootloader(agents)
