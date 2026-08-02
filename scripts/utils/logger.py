"""Centralized logging infrastructure with formatted terminal output."""

import logging
import sys
from typing import Optional


class TerminalFormatter(logging.Formatter):
    """Custom logging formatter for clean terminal output with ANSI colors."""

    COLOR_RESET = "\033[0m"
    COLOR_BLUE = "\033[94m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_RED = "\033[91m"
    COLOR_CYAN = "\033[96m"

    FORMATS = {
        logging.DEBUG: COLOR_CYAN + "[DEBUG] %(message)s" + COLOR_RESET,
        logging.INFO: COLOR_GREEN + "[INFO] %(message)s" + COLOR_RESET,
        logging.WARNING: COLOR_YELLOW + "[WARN] %(message)s" + COLOR_RESET,
        logging.ERROR: COLOR_RED + "[ERROR] %(message)s" + COLOR_RESET,
        logging.CRITICAL: COLOR_RED + "[CRIT] %(message)s" + COLOR_RESET,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log message using color scheme."""
        log_fmt = self.FORMATS.get(record.levelno, "%(message)s")
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(name: str = "profile_builder") -> logging.Logger:
    """Retrieve or configure named logger singleton instance.

    Args:
        name: Name identifier for the logger instance.

    Returns:
        Configured Logger object.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(TerminalFormatter())
        logger.addHandler(handler)
    return logger
