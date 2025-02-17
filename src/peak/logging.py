import logging

logger = logging.getLogger("peak")
logger.addHandler(logging.NullHandler())

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")