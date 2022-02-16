import sys

from peak.mas.cli.parser import config, general


def main(args = None):
    if not args:
        args = sys.argv[1:]
        
    if len(args) == 1:
        config.parse(args)
    
    if len(args) > 1:
        general.parse(args)
    
