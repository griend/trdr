import datetime
import logging
import logging.handlers
import os
import sys
from pathlib import Path

import yaml

config = {}


def __init_directories(config: hash) -> None:
    trader_dir = os.path.join(Path.home(), 'var', 'trader')
    db_dir = os.path.join(trader_dir, 'db')
    etc_dir = os.path.join(trader_dir, 'etc')
    log_dir = os.path.join(trader_dir, 'log')
    tmp_dir = os.path.join(trader_dir, 'tmp')

    for directory in [db_dir, etc_dir, log_dir, tmp_dir]:
        if not os.path.isdir(directory):
            os.makedirs(directory)

    config['db_dir'] = db_dir
    config['etc_dir'] = etc_dir
    config['log_dir'] = log_dir
    config['tmp_dir'] = tmp_dir


def __init_config(config: hash) -> None:
    file = os.path.join(config['etc_dir'], 'config.yaml')

    if os.path.isfile(file):
        with open(file) as f:
            data = yaml.safe_load(f)

        config['bitvavo_api_key'] = data['BITVAVO']['API_KEY']
        config['bitvavo_api_secret'] = data['BITVAVO']['API_SECRET']
        config['telegram_token'] = data['TELEGRAM']['TOKEN']
    else:
        raise FileNotFoundError(file)

    config['app_name'] = 'trader'
    config['db_filename'] = os.path.join(config['db_dir'], 'trader.db')


def __daily_log_filename():
    now = datetime.datetime.now()
    name = f'{config["app_name"]}-{now.strftime("%Y%m%d")}.log'
    filename = os.path.join(config['log_dir'], name)
    return filename


def __init_logging(config: hash) -> None:
    format = logging.Formatter('%(asctime)s %(name)s %(levelname)s - %(message)s')

    fh = logging.handlers.TimedRotatingFileHandler(filename=__daily_log_filename(), when="d")
    fh.rotation_filename = __daily_log_filename
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


__init_directories(config)
__init_config(config)
__init_logging(config)

if __name__ == '__main__':
    import pprint

    logger = logging.getLogger(__name__)

    try:
        logger.info(f'Start - {__file__}')

        pprint.pprint(config)

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)