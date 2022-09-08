from peak.mas.cli.parser import config, general


def main(args):
    if len(args) == 1:
        config.parse(args)

    if len(args) > 1:
        general.parse(args)
