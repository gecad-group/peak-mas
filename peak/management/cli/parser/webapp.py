from pynpm import NPMPackage
from pathlib import Path
from argparse import ArgumentParser
from peak import __name__ as peak_name
from os import sep, chdir

def parse(args = None):
    parser = ArgumentParser(prog = peak_name + ' management webapp')
    parser.add_argument('-p','--port', type=str, default='8080')
    parser.add_argument('-d', '--df', type=str, default='localhost:10000')

    ns = parser.parse_args(args)

    chdir('peak' + sep + 'management' + sep + 'webapp' + sep)

    env = Path('.env.local').absolute()
    with open(env, 'w') as f:
        f.write("VUE_APP_DF='" + ns.df + "'")

    file = Path('package.json').absolute()
    pkg = NPMPackage(str(file))
    pkg.run_script('serve', '--', '--port', ns.port)