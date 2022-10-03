from argparse import ArgumentError, ArgumentTypeError
from logging import getLevelName, getLogger
from multiprocessing import Process
from os import chdir
from pathlib import Path
import yaml

from peak import JID
from peak.bootloader import boot_agent


_logger = getLogger()

def agent_exec(
    file: Path,
    jid: JID,
    properties: Path = None,
    clones: int = 1,
    log_level: int = getLevelName("INFO"),
    verify_security: bool = False,
    *args,
    **kargs
):
    """Executes and configures a single agent.

    Args:
        file: Path to the agent's python file.
        properties: Path to the agent's properties python file.
        jid: JID of the agent.
        clones: Number of clones to be made.
        log_leve: Logging level.
        verify_security: Verifies the SSL certificates.

    Raises:
        ArgumentTypeError if the file provided is not a python file.
    """

    log_level = getLevelName(log_level)

    for f in [file, properties]:
        if f and not f.is_file():
            raise ArgumentTypeError("'{}' must be an existing python file".format(f))

    kwargs = {
        "file": file,
        "jid": jid,
        "name": jid.localpart,
        "number": None,
        "properties": properties,
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
    """Executes multiple agents using a YAML configuration file.

    Args:
        file: Path to the agent's python file.
    """
    defaults = {
        "file": None,
        "domain": None,
        "resource": None,
        "ssl": False,
        "log_level": "info",
        "properties": None,
        "clones": 1,
    }
    _logger.debug("parsing yaml file")
    with file.open() as f:
        yml = yaml.full_load(f)
    if "defaults" in yml:
        defaults = defaults | yml["defaults"]
    else:
        _logger.debug('no defaults in yaml file')
    if "agents" not in yml:
        raise Exception("agents argument required")
    if len(yml["agents"]) == 1:
        agent, args = yml["agents"].popitem()
        args = defaults | args
        if args["file"] is None:
            raise Exception(f"{agent}: file argument required")
        if args["domain"] is None:
            raise Exception(f"{agent}: domain argument required")
        args["jid"] = JID(agent, args["domain"], args["resource"])
        agent_exec(**args)
    else:
        _logger.debug("initialize processes")
        procs = []
        for agent, args in yml["agents"].items():
            args = defaults | args
            if args["file"] is None:
                raise Exception(f"{agent}: file argument required")
            if args["domain"] is None:
                raise Exception(f"{agent}: domain argument required")
            args["jid"] = JID(agent, args["domain"], args["resource"])
            proc = Process(target=agent_exec, kwargs=args, daemon=False)
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
    

