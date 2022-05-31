from pynpm import NPMPackage
from pathlib import Path
from argparse import ArgumentParser
import peak
import os

def parse(args = None):
    parser = ArgumentParser(prog = peak.__name__ + ' management webapp')
    parser.add_argument('-p','--port', type=str, default='8080')
    parser.add_argument('-d', '--df', type=str, default='localhost:10000')

    ns = parser.parse_args(args)

    webapp_path = 'peak' + os.sep + 'management' + os.sep + 'webapp' + os.sep

    env = Path(webapp_path + '.env.local').absolute()
    with open(env, 'w') as f:
        f.write("VUE_APP_DF='" + ns.df + "'")

    file = Path( webapp_path + 'package.json').absolute()
    pkg = NPMPackage(str(file))
    pkg.run_script('serve', '--', '--port', ns.port)