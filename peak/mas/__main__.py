from argparse import ArgumentParser, ArgumentError, ArgumentTypeError
import importlib
import logging
import os
from pathlib import Path
import subprocess
import sys
import time

import peak



def validate_files(*args):
    for arg in args:
        if arg and not Path(arg).is_file():
            raise ArgumentTypeError('\'{}\' must be an existing python file'.format(arg))

def get_class(file):
    path = str(file.parent.resolve())
    sys.path.append(path)
    module_str = str(file).split(os.sep)[-1].split('.')[0]
    module = importlib.import_module(module_str)
    return getattr(module, module_str)
    

def main(args = None):
    if not args:
        args = sys.argv[1:]
        
    if len(args) == 1:
        config_parser(args)
    
    if len(args) > 1:
        general_parser(args)
    

def general_parser(args = None):
    try:
        parser = ArgumentParser(prog = peak.__name__)
        parser.add_argument('file', type=Path)
        parser.add_argument('agent_name', type=str.lower)
        parser.add_argument('server', type=str)
        parser.add_argument('-p','--properties', type=Path)
        parser.add_argument('-r', '--repeat', type=int, default=1)
        parser.add_argument('-l', '--logging', type=str.upper, default='INFO')
        parser.add_argument('--verify_security', type=bool, default=False)
        
        ns = parser.parse_args(args)  #if args none it reads from the terminal
        
        validate_files(ns.file, ns.properties)
        
        #boot only one agent
        if ns.repeat == 1:
            os.makedirs(str(ns.file.parent) + '/logs', exist_ok = True)
            logging.basicConfig(filename=str(ns.file.parent) + '/logs/' + ns.agent_name + '.log', level=logging.getLevelName(ns.logging))
            agent = get_class(ns.file)
            if ns.properties:
                properties = get_class(ns.properties)(ns.agent_name)
                properties = properties.extract(ns.agent_name)
            else:
                properties = None
            agent_instance = agent(ns.agent_name, ns.server, properties, ns.verify_security)
            agent_instance.start(True).result()
            try:
                while agent_instance.is_alive():
                    time.sleep(10)
            except KeyboardInterrupt:
                agent_instance.stop()

        #boot more than one agent
        else:
            procs = []
            for i in range(ns.repeat):
                args = ['python', '-m', peak.__name__, 
                        ns.file,
                        ns.agent_name + str(i),
                        ns.server]
                if ns.properties:      args.extend(['-p', ns.properties]) 
                if ns.verify_security: args.extend(['--verify_security', ns.verify_security])
                proc = subprocess.Popen(args)
                procs.append(proc)

            #wait for processes
            try:
                for proc in procs:
                    proc.wait()
            except KeyboardInterrupt:
                for proc in procs:
                    proc.kill()
    except ArgumentError or ArgumentTypeError as e:
        print(e)

def config_parser(args=None):
    try:
        config_parser = ArgumentParser(prog = peak.__name__)
        config_parser.add_argument('config_file', type=Path)
        ns = config_parser.parse_args(args)
        procs = []

        with open(ns.config_file) as f:
            commands = f.read().splitlines()
        for command in commands:
            args = ['python', '-m', peak.__name__]
            args.extend(command.split(' '))
            proc = subprocess.Popen(args, cwd=str(ns.config_file.parent.absolute()))
            procs.append(proc)

        #wait for processes
        try:
            for proc in procs:
                proc.wait()
        except KeyboardInterrupt:
            for proc in procs:
                proc.kill()
    except ArgumentError or ArgumentTypeError as e:
        print(e)



if __name__ == '__main__':
    main()
