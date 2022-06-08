from argparse import ArgumentParser
from multiprocessing import Process
from os import chdir
from pathlib import Path

from peak import __name__ as peak_name
from peak.mas.cli.parser import general


def parse(args=None):
    config_parser = ArgumentParser(prog = peak_name)
    config_parser.add_argument('config_file', type=Path)
    ns = config_parser.parse_args(args)

    with open(ns.config_file) as f:
        commands = f.read().splitlines()
    chdir(ns.config_file.parent)

    if len(commands) == 1:
        general.parse(commands[0].strip().split(' '))
    else:
        for command in commands:
            command = command.strip().split(' ')
            proc = Process(target=general.parse, args=(command,))
            proc.daemon = False
            proc.start()
