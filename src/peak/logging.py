import logging
import sys
from typing import Optional

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(FORMATTER)
_logger.addHandler(_handler)


def getLogger(name: Optional[str], level: int = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FORMATTER)
    logger.addHandler(handler)
    return logger


def log(message: str, level: int = logging.INFO):
    _logger.log(level, message)
