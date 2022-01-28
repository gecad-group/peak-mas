import argparse
import importlib
import pathlib
import subprocess
import sys
import time

import platform


def wait(procs):
    try:
        for proc in procs:
            proc.wait()
    except KeyboardInterrupt:
        for proc in procs:
            proc.kill()

def validate_files(*args):
    for arg in args:
        if arg and not arg.is_file():
            raise argparse.ArgumentTypeError('\'{}\' must be an existing python file'.format(arg))

def get_class(file):
    path = str(file.parent.resolve())
    sys.path.append(path)
    module_str = str(file).split('/')[-1].split('.')[0]
    module = importlib.import_module(module_str)
    return getattr(module, module_str)

def boot_single(agent_file, name, server, properties_file, verify_security):
    agent = get_class(agent_file)
    if properties_file:
        properties = get_class(properties_file)(name)
        properties = properties.extract(name)
    else:
        properties = None
    agent_instance = agent(name, server, properties, verify_security)
    agent_instance.start(True).result()
    try:
        while agent_instance.is_alive():
            time.sleep(10)
    except KeyboardInterrupt:
        agent_instance.stop()

def main():
    parser = argparse.ArgumentParser(prog = platform.__name__)
    parser.add_argument('file', type=pathlib.Path)
    parser.add_argument('agent_name', type=str.lower)
    parser.add_argument('server', type=str)
    parser.add_argument('-p','--properties', type=pathlib.Path)
    parser.add_argument('-r', '--repeat', type=int, default=1)
    parser.add_argument('--verify_security', type=bool, default=False)
    ns = parser.parse_args()

    validate_files(ns.file, ns.properties)

    if ns.repeat == 1:
        boot_single(ns.file, ns.agent_name, ns.server, ns.properties, ns.verify_security)
    else:
        procs = []
        for i in range(ns.repeat):
            args = ['python', '-m', platform.__name__, 
                    ns.file,
                    ns.agent_name + str(i),
                    ns.server]
            if ns.properties:      args.extend(['-p', ns.properties]) 
            if ns.verify_security: args.extend(['--verify_security', ns.verify_security])
            proc = subprocess.Popen(args)
            procs.append(proc)
        wait(procs)


if __name__ == '__main__':
    try:
        main()
    except argparse.ArgumentTypeError as e:
        print(e.args)
