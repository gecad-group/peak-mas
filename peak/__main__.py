import logging
from sys import argv

from peak.cli import df, mas
from peak import __name__ as peak_name

from argparse import ArgumentParser


def main(args=None):
    parser = ArgumentParser(prog=peak_name)
    parser.add_argument('-version', action='version', version='PEAK 1.0')
    subparsers = parser.add_subparsers(required=True)

    # parser for DF agent
    df_parser = subparsers.add_parser(name='df', help='Executes Directory Facilitator agent.')
    df_parser.add_argument("-domain", type=str, default="localhost", help='XMPP domain to which the DF must register and login.')
    df_parser.add_argument("--verify_security", action='store_true', help='Verifies the SLL certificates.')
    df_parser.add_argument(
        "-log",
        type=lambda x: logging.getLevelName(str.upper(x)),
        default=logging.getLevelName("INFO"),
        help='Selects the logging level of the DF.'
    )
    df_parser.add_argument("-port", type=str, default="10000", help='Port to be opened for the REST API.')
    df_parser.set_defaults(func=df.exec)

    # parser for the agent execution
    run_parser = subparsers.add_parser(name='run', help='Executes PEAK agents.')
    args = parser.parse_args(args)

    if args[0].lower() == "run":
        mas.exec(args[1:])
    else:
        print("Help message - in development")


if __name__ == "__main__":
    logger = logging.getLogger(peak_name)
    try:
        main()
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        pass
