import sys
import logging
from typing import Union
from os import PathLike

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s") 


def configure_peak_logger(log_level: Union[int, str]) -> logging.Logger:
    """Configure logger 'peak' to log to terminal."""
    logger = logging.getLogger("peak")
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)
    return logger

def configure_agent_root_logger(log_level: Union[int, str], filename: Union[str, PathLike], mode: str, debug_mode: bool) -> logging.Logger:
    logger = logging.getLogger()
    file_handler = logging.FileHandler(filename, mode)
    file_handler.setFormatter(FORMATTER)
    if not debug_mode:
        file_handler.addFilter(logging.Filter("peak"))
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)
    return logger

def configure_single_agent_logging():
    #configure root logger to log to console
    logger = logging.getLogger()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    console_handler.addFilter(logging.Filter("peak"))
    #console_handler.addFilter(logging.Filter("root"))
    logger.addHandler(console_handler)
    
    #remove all handlers from peak logger to not print logs twice
    logger = logging.getLogger("peak")
    logger.handlers.clear()

def getLogger(name: str = None) -> logging.Logger:
    if name is None:
        return logging.getLogger("peak")
    return logging.getLogger(f"peak.{name}")

def log(msg: str, level: Union[int, str] = logging.INFO):
    """Logs to the terminal and to the file."""
    logging.getLogger("peak").log(level, msg)