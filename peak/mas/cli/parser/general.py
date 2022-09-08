from argparse import ArgumentParser, ArgumentTypeError
from copy import copy
from logging import getLevelName, getLogger
from multiprocessing import Process
from pathlib import Path

from aioxmpp import JID

from peak import __name__ as peak_name
from peak.mas.cli.bootloader import boot_agent


def parse(args=None):
    parser = ArgumentParser(prog=peak_name)
    parser.add_argument("file", type=Path)
    parser.add_argument("jid", type=JID.fromstr)
    parser.add_argument("-p", "--properties", type=Path)
    parser.add_argument("-r", "--repeat", type=int, default=1)
    parser.add_argument("-l", "--logging", type=str.upper, default=getLevelName("INFO"))
    parser.add_argument("--verify_security", type=bool, default=False)

    ns = parser.parse_args(args)  # if args none it reads from the terminal

    ns.logging = getLevelName(ns.logging)

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
