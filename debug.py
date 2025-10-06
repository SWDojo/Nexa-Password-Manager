import logging
import os

_LOGGER = None

def get_logger(log_file="debug.log"):
    """Returns a singleton logger instance for NexaDebug."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger("NexaDebug")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if not logger.hasHandlers():
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Console handler (optional, uncomment if needed)
        # ch = logging.StreamHandler()
        # ch.setLevel(logging.INFO)
        # ch.setFormatter(formatter)
        # logger.addHandler(ch)

    _LOGGER = logger
    return logger

def log_debug(message):
    """Logs a debug message."""
    get_logger().debug(message)

def log_info(message):
    """Logs an info message."""
    get_logger().info(message)

def log_error(message):
    """Logs an error message."""
    get_logger().error(message)