import logging
from time import sleep

from peak import DF


def exec(domain: str, verify_security: bool, port: int, *args, **kargs):
    """Executes the Directory Facilitator agent.

    Args:
        log_level: Logging level to be used in the DF's logs.
        domain: Domain to which connect the DF.
        verify_security: Verifies the SSL certificates.
        port: Port to be used by the DF REST API.
    """
    logger = logging.getLogger(__name__).parent
    logger.handlers[1].setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

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
