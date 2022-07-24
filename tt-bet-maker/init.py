import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def init_dotenv():
    load_dotenv('.env')


def init() -> None:
    """
    Init .env and logger
    :param file: filename to use to configure logger
    :return:
    """
    init_dotenv()

    # configure logger
    logger_name = os.getenv('LOGGER_NAME')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    # create directory
    log_path = os.path.join(os.getenv('LOGGER_DIR'), logger_name + '.log')
    if not os.path.exists(os.path.dirname(log_path)):
        Path(os.path.dirname(log_path)).mkdir(parents=True, exist_ok=True)
    # create a file handler
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter(
        '{[%(asctime)s] - %(name)s - %(levelname)s - %(funcName)s - line %(lineno)d}: %(message)s'
    )
    handler.setFormatter(formatter)

    # add handler to the logger
    logger.addHandler(handler)

    # add handler for stdout
    print_handler = logging.StreamHandler(sys.stdout)
    print_handler.setFormatter(formatter)
    print_handler.setLevel(logging.INFO)

    logger.addHandler(print_handler)
