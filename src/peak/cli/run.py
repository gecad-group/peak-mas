from argparse import ArgumentTypeError
from pathlib import Path

from peak import JID
from peak.bootloader import bootloader


def execute_agent(
    file: Path,
    jid: JID,
    clones: int,
    log_level: str,
    log_folder: Path,
    log_file_mode: str,
    debug_mode: bool = False,
    port: int = 5222,
    verify_security: bool = False,
    *args,
    **kargs,
):
    """Executes a single agent.

    Args:
        file: Path to the agent's python file.
        jid: JID of the agent.
        clones: Number of clones to be made.
        log_level: Logging level.
        verify_security: Verifies the SSL certificates.
    """
    # TODO: verify at argsparser level
    if file and not file.is_file():
        raise ArgumentTypeError(f"file argument must be a python file, not '{file}'")

    kwargs = {
        "file": file,
        "jid": jid,
        "cid": 0,
        "log_level": log_level,
        "log_folder": log_folder,
        "log_file_mode": log_file_mode,
        "debug_mode": debug_mode,
        "port": port,
        "verify_security": verify_security,
    }

    name = jid.localpart
    agents = []
    for cid in range(clones):
        agent = kwargs.copy()
        agents.append(agent)
        kwargs["jid"] = kwargs["jid"].replace(localpart=f"{name}{cid}")
        kwargs["cid"] = cid
    bootloader(agents)
