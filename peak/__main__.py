import logging

from peak.mas.cli.main import main as mas_main

logger = logging.getLogger('peak')

def main(args=None):
    try:
        mas_main(args)
    except Exception as e:
        logger.error(e)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()