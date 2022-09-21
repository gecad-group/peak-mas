import logging
from time import sleep

from peak import DF


def exec(log_level: int, domain: str, verify_security: bool, port: int):
    """Executes the Directory Facilitator agent.

    Args:
        args: List of arguments to be used by the DF.
    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting DF")
    df = DF(domain, verify_security, port)
    df.start().result()
    logger.info("DF running")
    
    try:
        while df.is_alive():
            sleep(10)
    except KeyboardInterrupt:
        df.stop()
    logger.info("Stoped DF")
