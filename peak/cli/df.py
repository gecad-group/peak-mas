import logging
from time import sleep

from peak import DF


def exec(log_level: int, domain: str, verify_security: bool, port: int):
    """Executes the Directory Facilitator agent.

    Args:
        log_level: Logging level to be used in the DF's logs.
        domain: Domain to which connect the DF.
        verify_security: Verifies the SSL certificates.
        port: Port to be used by the DF REST API.
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
