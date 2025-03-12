import io
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from peak import JID
from peak import __name__ as peak_name
from peak import __version__ as version
from peak import configure_cli_logger
from peak.cli import df, run

_logger = logging.getLogger(__name__)


def main(args=None):
    try:
        configure_cli_logger()
        _logger.info("initiating PEAK")
        _main(args)
        _logger.info("PEAK terminated")
    except Exception as e:
        _logger.critical(e, exc_info=1)
    except KeyboardInterrupt:
        _logger.info("PEAK terminated (KeyboardInterrupt)")


def _main(args=None):
    _logger.info("parsing console arguments")
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
        help="execute a single-agent system using a Python script",
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
        "-o",
        "--log_file",
        type=io.TextIOWrapper,
        default=sys.stdout,
        help="file used for the logs (default: standard output)",
    )
    run_parser.add_argument(
        "--verify_security", action="store_true", help="verify SLL certificates"
    )
    run_parser.set_defaults(func=run.execute_agent)

    # parser for the "start" command
    start_parser = subparsers.add_parser(
        name="start",
        help="execute agents using an YAML configuration file",
    )
    start_parser.add_argument(
        "file",
        type=Path,
        help="YAML configuration file",
    )
    start_parser.set_defaults(func=run.execute_config_file)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    args = parser.parse_args(args)
    args.func(**vars(args))
