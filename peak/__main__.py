import logging
from sys import argv

from peak.cli import df, mas
from peak import JID
from peak import __name__ as peak_name

from argparse import ArgumentParser, FileType, SUPPRESS


def main(args=None):
    parser = ArgumentParser(prog=peak_name)
    parser.add_argument('-version', action='version', version='PEAK 1.0')
    subparsers = parser.add_subparsers(required=True)

    # parser for "df" command
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

    # parser for the "run" command
    run_parser = subparsers.add_parser(name='run', help='Executes PEAK agents. It is possible to execute in two different ways: using a configuration file (txt) and using a python file.')
    run_parser.add_argument("file", type=FileType('r'), help='This file can either be a txt configuration file or a python file. The configuration file contains instructions to run on or more agents. The Python file must contain a class of a single agent to be executed. The name of the class must be the same of the name of the file. In case of being a Python file, the jid option is required.')
    run_parser.add_argument("-jid", type=JID.fromstr, help='JID of the agent to be executed. Only required if the file is a Python file.')
    run_parser.add_argument("-properties", type=FileType('r'), default=SUPPRESS, help='Python file where the agent properties are located. It can only be used when the file is a Python file.')
    run_parser.add_argument("-repeat", type=int, default=1, help='The number of times to replicate the agent. The name of each agent will be the same as the JID but with the number of the corresponding clone to it (e.g. john_0@localhost, john_1@localhost). The numbering starts in zero. This option can only be used ')
    run_parser.add_argument(
        "-log", 
        type=lambda x: logging.getLevelName(str.upper(x)), 
        default=logging.getLevelName("INFO"),
        help='Selects the logging level of the DF.'
    )
    run_parser.add_argument("--verify_security", type=bool, default=False,
        help='Verifies the SLL certificates. Only needed '
    )
    run_parser.set_defaults(func=mas.exec)
    args = parser.parse_args(args)
    args.func(**vars(args))

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
