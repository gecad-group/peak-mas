import logging
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

from peak import JID
from peak import __name__ as peak_name
from peak import __version__ as version
from peak.cli import df, mas

sys.path.append(os.getcwd())
_logger = logging.getLogger(peak_name)


def main(args=None):
    _logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    _logger.addHandler(handler)
    try:
        _main(args)
    except Exception as e:
        _logger.critical(e, exc_info=1)
    except KeyboardInterrupt:
        _logger.info("Stoping PEAK: (reason: KeyboardInterrupt)")


def _main(args=None):
    parser = ArgumentParser(prog=peak_name)
    parser.add_argument("--version", action="version", version=version)
    subparsers = parser.add_subparsers(required=True)

    # parser for "df" command
    df_parser = subparsers.add_parser(
        name="df", help="execute Directory Facilitator agent"
    )
    df_parser.add_argument(
        "-domain",
        type=str,
        default="localhost",
        help="XMPP server domain (default: localhost)",
    )
    df_parser.add_argument(
        "--verify_security", action="store_true", help="verify SLL certificates"
    )
    df_parser.add_argument(
        "-log_level",
        type=str.upper,
        default="INFO",
        help="PEAK logging level (default: INFO)",
    )
    df_parser.add_argument(
        "-port",
        type=str,
        default="10000",
        help="REST API port (default: 10000)",
    )
    df_parser.set_defaults(func=df.exec)

    # parser for the "run" command
    run_parser = subparsers.add_parser(
        name="run",
        help="execute PEAK's agents",
    )
    run_parser.add_argument(
        "file",
        type=Path,
        help="Python file containing the class of the agent to be executed (the same name must be used in the class and in the file) ",
    )
    run_parser.add_argument(
        "-jid", type=JID.fromstr, help="agent XMPP ID", required=True
    )
    run_parser.add_argument(
        "-clones",
        type=int,
        default=1,
        help="number of clones",
    )
    run_parser.add_argument(
        "-log_level",
        type=str.upper,
        default="INFO",
        help="PEAK logging level (default: INFO)",
    )
    run_parser.add_argument(
        "--verify_security", action="store_true", help="verify SLL certificates"
    )
    run_parser.set_defaults(func=mas.agent_exec)

    # parser for the "start" command
    start_parser = subparsers.add_parser(
        name="start",
        help="execute a multiagent system using an YAML configuration file",
    )
    start_parser.add_argument(
        "file",
        type=Path,
        help="YAML configuration file",
    )
    start_parser.add_argument(
        "-log_level",
        type=str.upper,
        default="INFO",
        help="PEAK logging level (default: INFO)",
    )
    start_parser.set_defaults(func=mas.multi_agent_exec)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args(args)
    _logger.setLevel(args.log_level)
    _logger.info("Starting PEAK")
    args.func(**vars(args))
    _logger.info("Stoping PEAK")
