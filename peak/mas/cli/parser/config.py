from argparse import ArgumentParser
from multiprocessing import Process, Lock
import os
from pathlib import Path

import peak
from peak.mas.cli.parser import general


def parse(args=None):
    config_parser = ArgumentParser(prog = peak.__name__)
    config_parser.add_argument('config_file', type=Path)
    ns = config_parser.parse_args(args)
    procs = []
    lock = Lock()

    with open(ns.config_file) as f:
        commands = f.read().splitlines()
    os.chdir(ns.config_file.parent)
    for command in commands:
        
        lock.acquire()
        command = command.strip().split(' ')
        proc = Process(target=general.parse, args=(command, lock))
        proc.start()
        procs.append(proc)

    #wait for processes
    for proc in procs:
        try:
            proc.join()
        except KeyboardInterrupt:
            pass
