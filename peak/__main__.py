import logging
import sys

from peak.mas.cli.main import main as mas_main
from peak.management.cli.main import main as management_main

def main(args=None):
    logger = logging.getLogger('peak')
    try:
        if not args:
            args = sys.argv[1:]

        if args[0].lower() == 'management':
            management_main(args[1:])
        else:
            mas_main(args)

    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()