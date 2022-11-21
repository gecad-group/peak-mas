# Standard library imports
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

# Reader imports
from peak import JID
from peak import __name__ as peak_name, __version__ as version
from peak.cli import df, mas

logger = logging.getLogger()


def main(args=None):
    parser = ArgumentParser(prog=peak_name)
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument(
        "-v",
        action="store_true",
        help="Verbose. Turns on the debug info.",
    )
    subparsers = parser.add_subparsers(required=True)

    # parser for "df" command
    df_parser = subparsers.add_parser(
        name="df", help="Execute Directory Facilitator agent."
    )
    df_parser.add_argument(
        "-domain",
        type=str,
        default="localhost",
        help="XMPP domain to which the DF must register and login. Default is localhost.",
    )
    df_parser.add_argument(
        "--verify_security", action="store_true", help="Verifies the SLL certificates."
    )
    df_parser.add_argument(
        "-log_level",
        type=lambda x: logging.getLevelName(str.upper(x)),
        default=logging.getLevelName("INFO"),
        help="Selects the logging level of the DF. Default is INFO.",
    )
    df_parser.add_argument(
        "-port",
        type=str,
        default="10000",
        help="Port to be opened for the REST API. Default is 10000",
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
        "-clones",
        type=int,
        default=1,
        help="The number of clones of the agent. The name of each agent will be the same as the JID but with the number of the corresponding clone to it (e.g. john_0@localhost, john_1@localhost). The sequence starts in zero.",
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
        help="Executes multiple agents using a YAML configuration file.",
    )
    start_parser.add_argument(
        "file",
        type=Path,
        help="Path to the YAML configuration file.",
    )
    start_parser.set_defaults(func=mas.multi_agent_exec)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args(args)
    if args.v:
        logger.setLevel("DEBUG")
    args.func(**vars(args))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        pass
