from argparse import ArgumentParser, ArgumentTypeError
from copy import copy
from logging import getLevelName, getLogger
from multiprocessing import Process
from os import chdir
from pathlib import Path

from aioxmpp import JID

from peak import __name__ as peak_name
from peak.bootloader import boot_agent


def exec(args: list[str]):
    """Parses the arguments for agent execution.

    Args:
        args: List of arguments needed for executing agents.
    """
    if len(args) == 0 or args[0].lower() == "-h":
        print("Help message - in development")
    elif len(args) == 1:
        multi_agent_exec(args)
    elif len(args) > 1:
        agent_exec(args)


def agent_exec(args=None):
    """Executes and configures a single agent.

    Args:
        args: List of arguments for the agent configuration.

    Raises:
        ArgumentTypeError if the file provided is not a python file.
    """
    parser = ArgumentParser(prog=peak_name)
    parser.add_argument("file", type=Path)
    parser.add_argument("jid", type=JID.fromstr)
    parser.add_argument("-p", "--properties", type=Path)
    parser.add_argument("-r", "--repeat", type=int, default=1)
    parser.add_argument(
        "-l", "--log_level", type=str.upper, default=getLevelName("INFO")
    )
    parser.add_argument("--verify_security", type=bool, default=False)

    ns = parser.parse_args(args)  # if args none it reads from the terminal

    ns.log_level = getLevelName(ns.log_level)

    for file in [ns.file, ns.properties]:
        if file and not file.is_file():
            raise ArgumentTypeError("'{}' must be an existing python file".format(file))

    kwargs = copy(vars(ns))
    kwargs["name"] = ns.jid.localpart
    kwargs["number"] = None
    kwargs.pop("repeat")

    if ns.repeat == 1:
        boot_agent(**kwargs)
    else:
        procs = []
        for i in range(ns.repeat):
            kwargs["jid"] = ns.jid.replace(localpart=ns.jid.localpart + str(i))
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


def multi_agent_exec(args=None):
    """Executes multiple agents using a configuration file.

    For now it uses a txt file to configure the multi-agent system,
    but will be updated to a YAML file.

    Args:
        args: List with the path to the configuration file.
    """
    config_parser = ArgumentParser(prog=peak_name)
    config_parser.add_argument("config_file", type=Path)
    ns = config_parser.parse_args(args)

    with open(ns.config_file.absolute()) as f:
        commands = f.read().splitlines()
    chdir(ns.config_file.parent)

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
