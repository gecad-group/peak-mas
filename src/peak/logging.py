import logging
import sys
from os import PathLike
from typing import Union

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def configure_cli_logger() -> logging.Logger:
    """Configure logger for command line interface."""
    logger = logging.getLogger("peak")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)
    return logger


def configure_single_agent_logging(
    log_level: Union[int, str], filename: Union[str, PathLike], mode: str
) -> logging.Logger:
    """Configure logging for single agent."""
    logger = logging.getLogger("peak")
    logger.setLevel(log_level)
    logger.propagate = False
    logger.handlers.clear()
    file_handler = logging.FileHandler(filename, mode)
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)


def configure_multiple_agent_logging(
    log_level: Union[int, str], filename: Union[str, PathLike], mode: str
) -> logging.Logger:
    logger = logging.getLogger("peak")
    logger.setLevel(log_level)
    logger.propagate = False
    logger.handlers.clear()
    file_handler = logging.FileHandler(filename, mode)
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    logger = logging.getLogger("peak.main")
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)


def configure_debug_mode(
    log_level: Union[int, str], filename: Union[str, PathLike], mode: str
):
    """Configure 'root' logger to consume logs from all other modules
    using the 'peak' logger file handler. Only logs them to the file."""
    logger = logging.getLogger()
    logger.setLevel(log_level)
    file_handler = logging.FileHandler(filename, mode)
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)


def getLogger(name: str = None) -> logging.Logger:
    """Same as getFileLogger, just renamed it."""
    return getFileLogger(name)


def getFileLogger(name: str = None) -> logging.Logger:
    """Get 'peak' logger or a sublogger of 'peak.{name}'.
    Prints to the file. It only prints in the terminal if there
    is one agent running."""
    if name is None:
        return logging.getLogger("peak")
    return logging.getLogger(f"peak.{name}")


def getMainLogger(name: str = None) -> logging.Logger:
    """Get 'peak.main' logger. Always prints in the terminal."""
    if name is None:
        return logging.getLogger("peak.main")
    return logging.getLogger(f"peak.main.{name}")


def log(msg: str, level: Union[int, str] = logging.INFO):
    """Logs to the file. Default level info."""
    logging.getLogger("peak").log(level, msg)


def debug(msg: str, level: Union[int, str] = logging.DEBUG):
    """Logs to the terminal. Default level debug."""
    logging.getLogger("peak.main").log(level, msg)
