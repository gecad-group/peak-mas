from argparse import ArgumentTypeError
from logging import getLevelName, getLogger
from multiprocessing import Process
from os import chdir
from pathlib import Path

from peak import JID
from peak.bootloader import boot_agent


def agent_exec(
    file: Path,
    properties: Path,
    jid: JID,
    repeat: int,
    log_level: int,
    verify_security: bool,
):
    """Executes and configures a single agent.

    Args:
        file: Path to the agent's python file.
        properties: Path to the agent's properties python file.
        jid: JID of the agent.
        repeat: Number of clones to be made.
        log_leve: Logging level.
        verify_security: Verifies the SSL certificates.

    Raises:
        ArgumentTypeError if the file provided is not a python file.
    """

    log_level = getLevelName(log_level)

    for file in [file, properties]:
        if file and not file.is_file():
            raise ArgumentTypeError("'{}' must be an existing python file".format(file))

    kwargs = {
        "file": file,
        "jid": jid,
        "name": jid.localpart,
        "number": None,
        "properties": properties,
        "log_level": log_level,
        "verify_security": verify_security,
    }

    if repeat == 1:
        boot_agent(**kwargs)
    else:
        procs = []
        for i in range(repeat):
            kwargs["jid"] = jid.replace(localpart=jid.localpart + str(i))
            kwargs["number"] = i
            proc = Process(target=boot_agent, kwargs=kwargs, daemon=False)
            proc.start()
            procs.append(proc)
        try:
            logger = getLogger(__name__)
            [proc.join() for proc in procs]
        except Exception as e:
            logger.exception(e)
        except KeyboardInterrupt:
            pass


def multi_agent_exec(file: Path):
    """Executes multiple agents using a configuration file.

    For now it uses a txt file to configure the multi-agent system,
    but will be updated to a YAML file.

    Args:
        file: Path to the agent's python file.
    """

    with open(file.absolute()) as f:
        commands = f.read().splitlines()
    chdir(file.parent)

    if len(commands) == 1:
        agent_exec(commands[0].strip().split(" "))
    else:
        procs = []
        for command in commands:
            command = command.strip().split(" ")
            proc = Process(target=agent_exec, args=[command], daemon=False)
            proc.start()
            procs.append(proc)
        try:
            logger = getLogger(__name__)
            [proc.join() for proc in procs]
        except Exception as e:
            logger.exception(e)
        except KeyboardInterrupt:
            pass
