from argparse import ArgumentParser
from multiprocessing import Process
from logging import getLogger
from os import chdir
from pathlib import Path

from peak import __name__ as peak_name
from peak.mas.cli.parser.general import parse as general_parse


def parse(args=None):
    config_parser = ArgumentParser(prog = peak_name)
    config_parser.add_argument('config_file', type=Path)
    ns = config_parser.parse_args(args)

    with open(ns.config_file.absolute()) as f:
        commands = f.read().splitlines()
    chdir(ns.config_file.parent)

    if len(commands) == 1:
        general_parse(commands[0].strip().split(' '))
    else:
        procs = []
        for command in commands:
            command = command.strip().split(' ')
            proc = Process(target=general_parse, args=[command], daemon=False)
            proc.start()
            procs.append(proc)
        try:
            logger = getLogger(__name__)
            [proc.join() for proc in procs]
        except Exception as e:
            logger.exception(e)
        except KeyboardInterrupt:
            pass
