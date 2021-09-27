import logging
import logging.handlers
import os
import time
import datetime
from pathlib import Path
import sys

logger = logging.getLogger(__name__)
config = {}

def __init_directories() -> None:
    poc_dir = os.path.join(Path.home(), 'var', 'poc')
    log_dir = os.path.join(poc_dir, 'log')

    for directory in [log_dir]:
        if not os.path.isdir(directory):
            os.makedirs(directory)

    config['app_name'] = 'poc'
    config['log_dir'] = log_dir


def __daily_filename():
    now = datetime.datetime.now()
    name = f'{config["app_name"]}-{now.strftime("%Y%m%d-%H%M")}.log'
    filename = os.path.join(config['log_dir'], name)
    return filename


def __init_logging() -> None:
    format = logging.Formatter('%(asctime)s %(name)s %(levelname)s - %(message)s')

    filename = os.path.join(config['log_dir'], 'poc.log')
    fh = logging.handlers.TimedRotatingFileHandler(filename, when="M", interval=1, backupCount=5)
    fh.setFormatter(format)
    fh.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setFormatter(format)

    if sys.stdout.isatty():
        console.setLevel(logging.INFO)
    else:
        console.setLevel(logging.FATAL)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(fh)
    logger.addHandler(console)


if __name__ == '__main__':
    __init_directories()
    __init_logging()

    try:
        logger.info(f'Start - {__file__}')
        logger.info(f'PID: {os.getpid()}')

        for n in range(600):
            logger.info(f'{n:3} Sleeping...')
            time.sleep(1)

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
