from pynpm import NPMPackage
from pathlib import Path

def parse(args = None):
    file = Path('peak/management/webapp/package.json').absolute()
    pkg = NPMPackage(str(file))
    pkg.run_script('serve')