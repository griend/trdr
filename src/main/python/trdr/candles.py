'''
Continue receive crypto coin information from Bitvavo.
'''
import logging
import os
import pprint
import signal
import sqlite3
import time

from python_bitvavo_api.bitvavo import Bitvavo

from . import config, init_logging
from .trader import connect

logger = logging.getLogger(__name__)
running = True

market_cache = {}
candle_cache = {}


def signal_handler(signum, frame) -> None:
    '''
    A SIGTERM is received from the operating system.

    :param signum:
    :param frame:
    '''
    global running
    logger.debug(f'handler() - Start')

    running = False
    logger.info(f'Stopping...')

    logger.debug(f'handler() - Finish')


def populate_markets() -> None:
    '''
    Fill the cache with markets metadata.
    '''
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
          SELECT id,
                 market
            FROM markets
           WHERE status = 'trading'
        ORDER BY market
    ''')
    markets = cursor.fetchall()
    for market in markets:
        market_cache[market['market']] = market['id']
    cursor.close()
    connection.commit()
    connection.close()


def populate_candle_1m() -> None:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
       SElECT *
         FROM (
            SELECT c.timestamp AS timestamp,
                   m.market AS market,
                   c.open AS open,
                   c.high AS high,
                   c.low AS low,
                   c.close AS close,
                   c.volume AS volume
              FROM candle1m c
              JOIN markets m
                    ON m.id = c.market_id
           ORDER BY c.timestamp desc, c.market_id desc
              LIMIT 20
        )
        ORDER BY timestamp, market
    ''')
    candles = cursor.fetchall()
    for candle in candles:
        timestamp = candle['timestamp']
        market = candle['market']
        open = candle['open']
        high = candle['high']
        low = candle['low']
        close = candle['close']
        volume = candle['volume']
        if market not in candle_cache:
            candle_cache[market] = {}
        if '1m' not in candle_cache[market]:
            candle_cache[market]['1m'] = {}
        candle_cache[market]['1m']['timestamp'] = timestamp
        candle_cache[market]['1m']['open'] = open
        candle_cache[market]['1m']['high'] = high
        candle_cache[market]['1m']['low'] = low
        candle_cache[market]['1m']['close'] = close
        candle_cache[market]['1m']['volume'] = volume
    cursor.close()
    connection.commit()
    connection.close()


def populate_candle_5m() -> None:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
       SElECT *
         FROM (
            SELECT c.timestamp AS timestamp,
                   m.market AS market,
                   c.open AS open,
                   c.high AS high,
                   c.low AS low,
                   c.close AS close,
                   c.volume AS volume
              FROM candle5m c
              JOIN markets m
                    ON m.id = c.market_id
           ORDER BY c.timestamp desc, c.market_id desc
              LIMIT 20
        )
        ORDER BY timestamp, market
    ''')
    candles = cursor.fetchall()
    for candle in candles:
        timestamp = candle['timestamp']
        market = candle['market']
        open = candle['open']
        high = candle['high']
        low = candle['low']
        close = candle['close']
        volume = candle['volume']
        if market not in candle_cache:
            candle_cache[market] = {}
        if '5m' not in candle_cache[market]:
            candle_cache[market]['5m'] = {}
        candle_cache[market]['5m']['timestamp'] = timestamp
        candle_cache[market]['5m']['open'] = open
        candle_cache[market]['5m']['high'] = high
        candle_cache[market]['5m']['low'] = low
        candle_cache[market]['5m']['close'] = close
        candle_cache[market]['5m']['volume'] = volume
    cursor.close()
    connection.commit()
    connection.close()


def populate_candle_1h() -> None:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
       SElECT *
         FROM (
            SELECT c.timestamp AS timestamp,
                   m.market AS market,
                   c.open AS open,
                   c.high AS high,
                   c.low AS low,
                   c.close AS close,
                   c.volume AS volume
              FROM candle1h c
              JOIN markets m
                    ON m.id = c.market_id
           ORDER BY c.timestamp desc, c.market_id desc
              LIMIT 20
        )
        ORDER BY timestamp, market
    ''')
    candles = cursor.fetchall()
    for candle in candles:
        timestamp = candle['timestamp']
        market = candle['market']
        open = candle['open']
        high = candle['high']
        low = candle['low']
        close = candle['close']
        volume = candle['volume']
        if market not in candle_cache:
            candle_cache[market] = {}
        if '1h' not in candle_cache[market]:
            candle_cache[market]['1h'] = {}
        candle_cache[market]['1h']['timestamp'] = timestamp
        candle_cache[market]['1h']['open'] = open
        candle_cache[market]['1h']['high'] = high
        candle_cache[market]['1h']['low'] = low
        candle_cache[market]['1h']['close'] = close
        candle_cache[market]['1h']['volume'] = volume
    cursor.close()
    connection.commit()
    connection.close()


def populate_candle_1d() -> None:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
       SElECT *
         FROM (
            SELECT c.timestamp AS timestamp,
                   m.market AS market,
                   c.open AS open,
                   c.high AS high,
                   c.low AS low,
                   c.close AS close,
                   c.volume AS volume
              FROM candle1d c
              JOIN markets m
                    ON m.id = c.market_id
           ORDER BY c.timestamp desc, c.market_id desc
              LIMIT 20
        )
        ORDER BY timestamp, market
    ''')
    candles = cursor.fetchall()
    for candle in candles:
        timestamp = candle['timestamp']
        market = candle['market']
        open = candle['open']
        high = candle['high']
        low = candle['low']
        close = candle['close']
        volume = candle['volume']
        if market not in candle_cache:
            candle_cache[market] = {}
        if '1d' not in candle_cache[market]:
            candle_cache[market]['1d'] = {}
        candle_cache[market]['1d']['timestamp'] = timestamp
        candle_cache[market]['1d']['open'] = open
        candle_cache[market]['1d']['high'] = high
        candle_cache[market]['1d']['low'] = low
        candle_cache[market]['1d']['close'] = close
        candle_cache[market]['1d']['volume'] = volume
    cursor.close()
    connection.commit()
    connection.close()


def insert_1m(timestamp: int, market_id: int, open: float, high: float, low: float, close: float,
              volume: float) -> None:
    logger.debug('insert_1m() - Start')
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO candle1m (
            timestamp,
            market_id,
            open,
            high,
            low,
            close,
            volume
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp,
        market_id,
        open,
        high,
        low,
        close,
        volume,
    ))
    cursor.close()
    connection.commit()
    connection.close()
    logger.debug('insert_1m() - Finish')


def update_1m(timestamp: int, market_id: int, open: float, high: float, low: float, close: float,
              volume: float) -> None:
    logger.debug('update_1m() - Start')
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
           UPDATE candle1m
              SET open = ?,
                  high = ?,
                  low = ?,
                  close = ?,
                  volume = ?
            WHERE timestamp = ?
              AND market_id = ?
        ''', (
        open,
        high,
        low,
        close,
        volume,
        timestamp,
        market_id,
    ))
    cursor.close()
    connection.commit()
    connection.close()
    logger.debug('update_1m() - Finish')


def insert_5m(timestamp: int, market_id: int, open: float, high: float, low: float, close: float,
              volume: float) -> None:
    logger.debug('insert_5m() - Start')
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO candle5m (
            timestamp,
            market_id,
            open,
            high,
            low,
            close,
            volume
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp,
        market_id,
        open,
        high,
        low,
        close,
        volume,
    ))
    cursor.close()
    connection.commit()
    connection.close()
    logger.debug('insert_5m() - Finish')


def update_5m(timestamp: int, market_id: int, open: float, high: float, low: float, close: float,
              volume: float) -> None:
    logger.debug('update_5m() - Start')
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
           UPDATE candle5m
              SET open = ?,
                  high = ?,
                  low = ?,
                  close = ?,
                  volume = ?
            WHERE timestamp = ?
              AND market_id = ?
    ''', (
        open,
        high,
        low,
        close,
        volume,
        timestamp,
        market_id,
    ))
    cursor.close()
    connection.commit()
    connection.close()
    logger.debug('update_5m() - Finish')


def insert_1h(timestamp: int, market_id: int, open: float, high: float, low: float, close: float,
              volume: float) -> None:
    logger.debug('insert_1h() - Start')
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO candle1h (
            timestamp,
            market_id,
            open,
            high,
            low,
            close,
            volume
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
        timestamp,
        market_id,
        open,
        high,
        low,
        close,
        volume,
    ))
    cursor.close()
    connection.commit()
    connection.close()
    logger.debug('insert_1h() - Finish')


def update_1h(timestamp: int, market_id: int, open: float, high: float, low: float, close: float,
              volume: float) -> None:
    logger.debug('update_1h() - Start')
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
           UPDATE candle1h
              SET open = ?,
                  high = ?,
                  low = ?,
                  close = ?,
                  volume = ?
            WHERE timestamp = ?
              AND market_id = ?
        ''', (
        open,
        high,
        low,
        close,
        volume,
        timestamp,
        market_id,
    ))
    cursor.close()
    connection.commit()
    connection.close()
    logger.debug('update_1h() - Finish')


def insert_1d(timestamp: int, market_id: int, open: float, high: float, low: float, close: float,
              volume: float) -> None:
    logger.debug('insert_1d() - Start')
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO candle1d (
            timestamp,
            market_id,
            open,
            high,
            low,
            close,
            volume
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
        timestamp,
        market_id,
        open,
        high,
        low,
        close,
        volume,
    ))
    cursor.close()
    connection.commit()
    connection.close()
    logger.debug('insert_1d() - Finish')


def update_1d(timestamp: int, market_id: int, open: float, high: float, low: float, close: float,
              volume: float) -> None:
    logger.debug('update_1d() - Start')
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
           UPDATE candle1d
              SET open = ?,
                  high = ?,
                  low = ?,
                  close = ?,
                  volume = ?
            WHERE timestamp = ?
              AND market_id = ?
        ''', (
        open,
        high,
        low,
        close,
        volume,
        timestamp,
        market_id,
    ))
    cursor.close()
    connection.commit()
    connection.close()
    logger.debug('update_1d() - Finish')


def callback_1m(response):
    logger.debug('callback_1m() - Start')
    try:
        market = response['market']
        timestamp = int(response['candle'][0][0] / 1000)
        market_id = market_cache[market]
        open = float(response['candle'][0][1])
        high = float(response['candle'][0][2])
        low = float(response['candle'][0][3])
        close = float(response['candle'][0][4])
        volume = float(response['candle'][0][5])

        if market not in candle_cache:
            candle_cache[market] = {}
            candle_cache[market]['1m'] = {}
            candle_cache[market]['1m']['timestamp'] = 0
            is_new = True
        elif '1m' not in candle_cache[market]:
            candle_cache[market]['1m'] = {}
            candle_cache[market]['1m']['timestamp'] = 0
            is_new = True
        elif 'timestamp' not in candle_cache[market]['1m']:
            candle_cache[market]['1m']['timestamp'] = 0
            is_new = True
        elif candle_cache[market]['1m']['timestamp'] == timestamp:
            is_new = False
        elif candle_cache[market]['1m']['timestamp'] != timestamp:
            is_new = True
        else:
            logger.error(f'callback1m(): {market} {timestamp}')
            return

        if is_new:
            if candle_cache[market]['1m']['timestamp'] > 0:
                logger.info(
                    f"{candle_cache[market]['1m']['timestamp']} 1m " +
                    f"{market} " +
                    f"{candle_cache[market]['1m']['open']} " +
                    f"{candle_cache[market]['1m']['high']} " +
                    f"{candle_cache[market]['1m']['low']} " +
                    f"{candle_cache[market]['1m']['close']} " +
                    f"{candle_cache[market]['1m']['volume']}")
            insert_1m(timestamp, market_id, open, high, low, close, volume)
        else:
            update_1m(timestamp, market_id, open, high, low, close, volume)

        candle_cache[market]['1m']['timestamp'] = timestamp
        candle_cache[market]['1m']['open'] = open
        candle_cache[market]['1m']['high'] = high
        candle_cache[market]['1m']['low'] = low
        candle_cache[market]['1m']['close'] = close
        candle_cache[market]['1m']['volume'] = volume
    except Exception as e:
        logger.error(e, exc_info=True)

    logger.debug('callback_1m() - Finish')


def callback_5m(response):
    logger.debug('callback_5m() - Start')
    try:
        market = response['market']
        timestamp = int(response['candle'][0][0] / 1000)
        market_id = market_cache[market]
        open = float(response['candle'][0][1])
        high = float(response['candle'][0][2])
        low = float(response['candle'][0][3])
        close = float(response['candle'][0][4])
        volume = float(response['candle'][0][5])

        if market not in candle_cache:
            candle_cache[market] = {}
            candle_cache[market]['5m'] = {}
            candle_cache[market]['5m']['timestamp'] = 0
            is_new = True
        elif '5m' not in candle_cache[market]:
            candle_cache[market]['5m'] = {}
            candle_cache[market]['5m']['timestamp'] = 0
            is_new = True
        elif 'timestamp' not in candle_cache[market]['5m']:
            candle_cache[market]['5m']['timestamp'] = 0
            is_new = True
        elif candle_cache[market]['5m']['timestamp'] == timestamp:
            is_new = False
        elif candle_cache[market]['5m']['timestamp'] != timestamp:
            is_new = True
        else:
            logger.error(f'callback_5m(): {market} {timestamp}')
            return

        if is_new:
            if candle_cache[market]['5m']['timestamp'] > 0:
                logger.info(
                    f"{candle_cache[market]['5m']['timestamp']} 5m " +
                    f"{market} " +
                    f"{candle_cache[market]['5m']['open']} " +
                    f"{candle_cache[market]['5m']['high']} " +
                    f"{candle_cache[market]['5m']['low']} " +
                    f"{candle_cache[market]['5m']['close']} " +
                    f"{candle_cache[market]['5m']['volume']}")
            insert_5m(timestamp, market_id, open, high, low, close, volume)
        else:
            update_5m(timestamp, market_id, open, high, low, close, volume)

        candle_cache[market]['5m']['timestamp'] = timestamp
        candle_cache[market]['5m']['open'] = open
        candle_cache[market]['5m']['high'] = high
        candle_cache[market]['5m']['low'] = low
        candle_cache[market]['5m']['close'] = close
        candle_cache[market]['5m']['volume'] = volume
    except Exception as e:
        logger.error(e, exc_info=True)
    logger.debug('callback_5m() - Finish')


def callback_1h(response):
    logger.debug('callback_1h() - Start')
    try:
        market = response['market']
        timestamp = int(response['candle'][0][0] / 1000)
        market_id = market_cache[market]
        open = float(response['candle'][0][1])
        high = float(response['candle'][0][2])
        low = float(response['candle'][0][3])
        close = float(response['candle'][0][4])
        volume = float(response['candle'][0][5])

        if market not in candle_cache:
            candle_cache[market] = {}
            candle_cache[market]['1h'] = {}
            candle_cache[market]['1h']['timestamp'] = 0
            is_new = True
        elif '1h' not in candle_cache[market]:
            candle_cache[market]['1h'] = {}
            candle_cache[market]['1h']['timestamp'] = 0
            is_new = True
        elif 'timestamp' not in candle_cache[market]['1h']:
            candle_cache[market]['1h']['timestamp'] = 0
            is_new = True
        elif candle_cache[market]['1h']['timestamp'] == timestamp:
            is_new = False
        elif candle_cache[market]['1h']['timestamp'] != timestamp:
            is_new = True
        else:
            logger.error(f'callback_1h(): {market} {timestamp}')
            return

        if is_new:
            if candle_cache[market]['1h']['timestamp'] > 0:
                logger.info(
                    f"{candle_cache[market]['1h']['timestamp']} 1h " +
                    f"{market} " +
                    f"{candle_cache[market]['1h']['open']} " +
                    f"{candle_cache[market]['1h']['high']} " +
                    f"{candle_cache[market]['1h']['low']} " +
                    f"{candle_cache[market]['1h']['close']} " +
                    f"{candle_cache[market]['1h']['volume']}")
            insert_1h(timestamp, market_id, open, high, low, close, volume)
        else:
            update_1h(timestamp, market_id, open, high, low, close, volume)

        candle_cache[market]['1h']['timestamp'] = timestamp
        candle_cache[market]['1h']['open'] = open
        candle_cache[market]['1h']['high'] = high
        candle_cache[market]['1h']['low'] = low
        candle_cache[market]['1h']['close'] = close
        candle_cache[market]['1h']['volume'] = volume
    except Exception as e:
        logger.error(e, exc_info=True)
    logger.debug('callback_1h() - Finish')


def callback_1d(response):
    logger.debug('callback_1d() - Start')
    try:
        market = response['market']
        timestamp = int(response['candle'][0][0] / 1000)
        market_id = market_cache[market]
        open = float(response['candle'][0][1])
        high = float(response['candle'][0][2])
        low = float(response['candle'][0][3])
        close = float(response['candle'][0][4])
        volume = float(response['candle'][0][5])

        if market not in candle_cache:
            candle_cache[market] = {}
            candle_cache[market]['1d'] = {}
            candle_cache[market]['1d']['timestamp'] = 0
            is_new = True
        elif '1d' not in candle_cache[market]:
            candle_cache[market]['1d'] = {}
            candle_cache[market]['1d']['timestamp'] = 0
            is_new = True
        elif 'timestamp' not in candle_cache[market]['1d']:
            candle_cache[market]['1d']['timestamp'] = 0
            is_new = True
        elif candle_cache[market]['1d']['timestamp'] == timestamp:
            is_new = False
        elif candle_cache[market]['1d']['timestamp'] != timestamp:
            is_new = True
        else:
            logger.error(f'callback_1d(): {market} {timestamp}')
            return

        if is_new:
            if candle_cache[market]['1d']['timestamp'] > 0:
                logger.info(
                    f"{candle_cache[market]['1d']['timestamp']} 1d " +
                    f"{market} " +
                    f"{candle_cache[market]['1d']['open']} " +
                    f"{candle_cache[market]['1d']['high']} " +
                    f"{candle_cache[market]['1d']['low']} " +
                    f"{candle_cache[market]['1d']['close']} " +
                    f"{candle_cache[market]['1d']['volume']}")
            insert_1d(timestamp, market_id, open, high, low, close, volume)
        else:
            update_1d(timestamp, market_id, open, high, low, close, volume)

        candle_cache[market]['1d']['timestamp'] = timestamp
        candle_cache[market]['1d']['open'] = open
        candle_cache[market]['1d']['high'] = high
        candle_cache[market]['1d']['low'] = low
        candle_cache[market]['1d']['close'] = close
        candle_cache[market]['1d']['volume'] = volume
    except Exception as e:
        logger.error(e, exc_info=True)
    logger.debug('callback_1d() - Finish')


def errorCallback(error):
    action = error['action']
    code = int(error['errorCode'])
    message = error['error']

    logger.error(f'Action: {action}, Code: {code}, Error: {message}')


def candle(bitvavo: Bitvavo) -> None:
    logger.debug('candle() - Start')

    websocket = bitvavo.newWebsocket()
    websocket.setErrorCallback(errorCallback)

    subscriptions = [
        'BTC-EUR',
        'ETH-EUR',
    ]

    for subscription in subscriptions:
        websocket.subscriptionCandles(subscription, '1m', callback_1m)
        websocket.subscriptionCandles(subscription, '5m', callback_5m)
        websocket.subscriptionCandles(subscription, '1h', callback_1h)
        websocket.subscriptionCandles(subscription, '1d', callback_1d)

    while running:
        time.sleep(1)

    logger.debug('candle() - Finish')


if __name__ == '__main__':
    init_logging(os.path.join(config['log_dir'], 'candles.log'))

    try:
        logger.info(f'Start - {__file__}')
        logger.info(f'PID: {os.getpid()}')

        signal.signal(signal.SIGTERM, signal_handler)

        # cache markets metadata
        populate_markets()

        # cache current values
        populate_candle_1m()
        populate_candle_5m()
        populate_candle_1h()
        populate_candle_1d()

        bitvavo = connect(config)
        candle(bitvavo)

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
