import logging
from argparse import ArgumentParser
from pathlib import Path
import sys

from peak import JID
from peak import __name__ as peak_name
from peak.cli import df, mas


def main(args=None):
    parser = ArgumentParser(prog=peak_name)
    parser.add_argument("-version", action="version", version="PEAK 1.0")
    subparsers = parser.add_subparsers(required=True)

    # parser for "df" command
    df_parser = subparsers.add_parser(
        name="df", help="Execute Directory Facilitator agent."
    )
    df_parser.add_argument(
        "-domain",
        type=str,
        default="localhost",
        help="XMPP domain to which the DF must register and login.",
    )
    df_parser.add_argument(
        "--verify_security", action="store_true", help="Verifies the SLL certificates."
    )
    df_parser.add_argument(
        "-log_level",
        type=lambda x: logging.getLevelName(str.upper(x)),
        default=logging.getLevelName("INFO"),
        help="Selects the logging level of the DF.",
    )
    df_parser.add_argument(
        "-port", type=str, default="10000", help="Port to be opened for the REST API."
    )
    df_parser.set_defaults(func=df.exec)

    # parser for the "run" command
    run_parser = subparsers.add_parser(
        name="run",
        help="Execute PEAK's agents.",
    )
    run_parser.add_argument(
        "file",
        type=Path,
        help="This file must be a python file. The Python file must contain a class of a single agent to be executed. The name of the class must be the same of the name of the file. ",
    )
    run_parser.add_argument(
        "-jid", type=JID.fromstr, help="JID of the agent to be executed.", required=True
    )
    run_parser.add_argument(
        "-properties",
        type=Path,
        help="Python file where the agent properties are located.",
    )
    run_parser.add_argument(
        "-repeat",
        type=int,
        default=1,
        help="The number of times to replicate the agent. The name of each agent will be the same as the JID but with the number of the corresponding clone to it (e.g. john_0@localhost, john_1@localhost). The sequence starts in zero.",
    )
    run_parser.add_argument(
        "-log_level",
        type=lambda x: logging.getLevelName(str.upper(x)),
        default=logging.getLevelName("INFO"),
        help="Selects the logging level of the agent.",
    )
    run_parser.add_argument(
        "--verify_security", action="store_true", help="Verifies the SLL certificates."
    )
    run_parser.set_defaults(func=mas.agent_exec)

    # parser for the "run" command
    start_parser = subparsers.add_parser(
        name="start",
        help="Execute PEAK MAS using a configuration file.",
    )
    start_parser.add_argument(
        "file",
        type=Path,
        help="This must be a path to the PEAK MAS configuration file. The file must be txt.",
    )
    start_parser.set_defaults(func=mas.multi_agent_exec)
    
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args(args)
    args.func(**vars(args))


if __name__ == "__main__":
    logger = logging.getLogger(peak_name)
    try:
        main()
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        pass
