from logging import getLogger
from sys import argv

from peak.cli import df, mas
from peak import __name__ as peak_name


def main(args=None):
    if not args:
        args = argv[1:]
    if len(args) == 0 or args[0].lower() == "-h":
        print("Help message - in development")
    elif args[0].lower() == "df":
        df.exec(args[1:])
    elif args[0].lower() == "run":
        mas.exec(args[1:])
    else:
        print("Help message - in development")


if __name__ == "__main__":
    logger = getLogger(peak_name)
    try:
        main()
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        pass
