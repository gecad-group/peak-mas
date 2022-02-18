from copy import copy
import logging
from argparse import ArgumentParser, ArgumentTypeError
from multiprocessing import Process
from pathlib import Path

import peak
from aioxmpp import JID
from peak.mas.cli.bootloader import boot_agent


def parse(args = None):
    parser = ArgumentParser(prog = peak.__name__)
    parser.add_argument('file', type=Path)
    parser.add_argument('jid', type=JID.fromstr)
    parser.add_argument('-p','--properties', type=Path)
    parser.add_argument('-r', '--repeat', type=int, default=1)
    parser.add_argument('-l', '--logging', type=str.upper, default=logging.getLevelName('INFO'))
    parser.add_argument('--verify_security', type=bool, default=False)
    
    ns = parser.parse_args(args)  #if args none it reads from the terminal

    ns.logging = logging.getLevelName(ns.logging)
    
    for file in [ns.file, ns.properties]:
        if file and not file.is_file():
            raise ArgumentTypeError('\'{}\' must be an existing python file'.format(file))
    
    agent_name = ns.jid.localpart
    kwargs = copy(vars(ns))
    kwargs.pop('repeat')
    procs = []
    for i in range(ns.repeat):
        if ns.repeat != 1:
            ns.jid = ns.jid.replace(localpart=agent_name + str(i))
            print(ns.jid)
        proc = Process(target=boot_agent, kwargs=kwargs)
        proc.start()
        procs.append(proc)

    #wait for processes
    for proc in procs:
        try:
            proc.join()
        except KeyboardInterrupt:
            pass
