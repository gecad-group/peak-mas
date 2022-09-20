import logging
from argparse import ArgumentParser
from time import sleep

import peak
from peak import DF


def exec(args: list[str]):
    """Executes the Directory Facilitator agent.

    Args:
        args: List of arguments to be used by the DF.
    """
    logging.basicConfig(
        level=ns.log,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting DF")
    df = DF(ns.domain, ns.verify_security, ns.port)
    df.start().result()
    logger.info("DF running")
    
    try:
        while df.is_alive():
            sleep(10)
    except KeyboardInterrupt:
        df.stop()
    logger.info("Stoped DF")
