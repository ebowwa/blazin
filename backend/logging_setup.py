# logging_setup.py

import logging

def setup_logging():
    # Configure logging settings
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger
