from logging import getLogger
from sys import argv

import peak.cli.parser as parser
from peak import __name__ as peak_name


def main(args=None):
    if not args:
        args = argv[1:]
    parser.parse(args)


if __name__ == "__main__":
    logger = getLogger(peak_name)
    try:
        main()
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        pass
