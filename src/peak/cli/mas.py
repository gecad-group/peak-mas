# Standard library imports
from argparse import ArgumentError, ArgumentTypeError
from logging import getLevelName, getLogger
from multiprocessing import Process
from os import chdir
from pathlib import Path

# Third party imports
import yaml

# Reader imports
from peak import JID
from peak.bootloader import boot_agent

_logger = getLogger()


def agent_exec(
    file: Path,
    jid: JID,
    clones: int = 1,
    log_level: int = getLevelName("INFO"),
    verify_security: bool = False,
    *args,
    **kargs,
):
    """Executes an agent.

    Args:
        file: Path to the agent's python file.
        jid: JID of the agent.
        clones: Number of clones to be made.
        log_level: Logging level.
        verify_security: Verifies the SSL certificates.
    """

    log_level = getLevelName(log_level)
    if file and not file.is_file():
        raise ArgumentTypeError(f"Agent's file must be a python file, not '{file}'.")

    kwargs = {
        "file": file,
        "jid": jid,
        "name": jid.localpart,
        "number": None,
        "log_level": log_level,
        "verify_security": verify_security,
    }

    if clones == 1:
        boot_agent(**kwargs)
    else:
        procs = []
        for i in range(clones):
            kwargs["jid"] = jid.replace(localpart=jid.localpart + str(i))
            kwargs["number"] = i
            proc = Process(target=boot_agent, kwargs=kwargs, daemon=False)
            proc.start()
            procs.append(proc)
        for proc in procs:
            try:
                proc.join()
            except Exception as e:
                _logger.exception(e)
            except KeyboardInterrupt:
                break


def multi_agent_exec(file: Path, *args, **kargs):
    """Executes agents using a YAML configuration file.

    Args:
        file: Path to the agent's python file.
    """
    defaults = {
        "file": None,
        "domain": None,
        "resource": None,
        "ssl": False,
        "log_level": "info",
        "clones": 1,
    }
    _logger.debug("parsing yaml file")
    with file.open() as f:
        yml = yaml.full_load(f)
    chdir(file.parent)
    if "defaults" in yml:
        defaults = defaults | yml["defaults"]
    else:
        _logger.debug("no defaults in yaml file")
    if "agents" not in yml:
        raise Exception("agents argument required")
    _logger.debug("initialize processes")
    procs = []
    for agent, agent_args in yml["agents"].items():
        agent_args = defaults | agent_args

        if agent_args["file"] is None:
            raise Exception(f"{agent}: file argument required")
        if agent_args["domain"] is None:
            raise Exception(f"{agent}: domain argument required")
        agent_args["file"] = Path(agent_args["file"])
        agent_args["jid"] = JID(agent, agent_args["domain"], agent_args["resource"])
        agent_args["log_level"] = agent_args["log_level"].upper()

        proc = Process(target=agent_exec, kwargs=agent_args, daemon=False)
        proc.start()
        procs.append(proc)
    _logger.debug("wait for processes to finish")
    for proc in procs:
        try:
            proc.join()
        except Exception as e:
            _logger.exception(e)
        except KeyboardInterrupt:
            break
