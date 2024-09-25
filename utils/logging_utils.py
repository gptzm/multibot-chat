import logging

def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level)
    return logging.getLogger(__name__)
