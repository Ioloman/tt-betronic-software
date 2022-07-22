import logging
import os

from dotenv import load_dotenv


def init(file: str) -> str:
    """
    Init .env and logger
    :param file: filename to use to configure logger
    :return:
    """
    load_dotenv('.env')

    # configure logger
    logger_name = file.removesuffix('py')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    # create a file handler
    handler = logging.FileHandler(os.path.join(os.getenv('LOGGER_DIR'), logger_name + 'log'))
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter(
        '{[%(asctime)s] - %(name)s - %(levelname)s - %(funcName)s - line %(lineno)d}: %(message)s'
    )
    handler.setFormatter(formatter)

    # add handler to the logger
    logger.addHandler(handler)

    return logger_name
