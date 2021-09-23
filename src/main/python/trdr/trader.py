import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from python_bitvavo_api.bitvavo import Bitvavo

from . import config

logger = logging.getLogger(__name__)


def connect(config: hash) -> Bitvavo:
    logger.debug('connect() - Start')

    logger.debug('connecting')
    bitvavo = Bitvavo({
        'APIKEY': config['bitvavo_api_key'],
        'APISECRET': config['bitvavo_api_secret'],
        'RESTURL': 'https://api.bitvavo.com/v2',
        'WSURL': 'wss://ws.bitvavo.com/v2/',
        'ACCESSWINDOW': 10000,
        'DEBUGGING': False,
    })
    logger.info('connected')

    logger.debug('connect() - Finish')
    return bitvavo


def get_time(bitvavo: Bitvavo) -> datetime:
    logger.debug('time() - Start')

    response = bitvavo.time()
    time = response['time']
    timezone = ZoneInfo('Europe/Amsterdam')
    dt = datetime.fromtimestamp(time / 1000, timezone)

    logger.debug('time() - Finish')
    return dt


def get_eur(bitvavo: Bitvavo) -> float:
    logger.debug('get_eur() - Start')

    response = bitvavo.balance({'symbol': 'EUR'})
    amount = float(response[0]['available'])

    logger.debug('get_eur() - Finish')
    return amount

def get_price_btc(bitvavo: Bitvavo) -> float:
    logger.debug('get_eur() - Start')

    response = bitvavo.tickerPrice({'market': 'BTC-EUR'})
    price = float(response['price'])

    logger.debug('get_btc_eur() - Finish')
    return price



def get_btc(bitvavo: Bitvavo) -> float:
    logger.debug('get_btc() - Start')

    response = bitvavo.balance({'symbol': 'BTC'})
    amount = float(response[0]['available'])

    logger.debug('get_btc() - Finish')
    return amount


if __name__ == '__main__':
    try:
        logger.info(f'Start - {__file__}')

        bitvavo = connect(config)
        time = get_time(bitvavo)
        eur = get_eur(bitvavo)
        btc = get_btc(bitvavo)
        price_btc = get_price_btc(bitvavo)

        logger.info(f'Bitvavo Time: {time}')
        logger.info(f'EUR: € {eur:.02f}')
        logger.info(f'BTC: € {btc * price_btc:.02f} (₿ {btc:.09f} @ {price_btc:.02f})')
        logger.info(f'Total: € {eur + btc * price_btc:.02f}')

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
