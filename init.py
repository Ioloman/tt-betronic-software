import logging
import os
from pathlib import Path

from dotenv import load_dotenv


def init(file: str) -> str:
    """
    Init .env and logger
    :param file: filename to use to configure logger
    :return:
    """
    load_dotenv('.env')

    # configure logger
    logger_name = os.path.split(file)[1].removesuffix('.py')
    logger = logging.getLogger(__name__)
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

    return logger_name
