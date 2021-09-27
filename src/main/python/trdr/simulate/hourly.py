import logging
import sqlite3
from datetime import datetime
import time

from .. import config

logger = logging.getLogger(__name__)

def get_rsi(candles: list) -> float:
    if len(candles) < 15:
        raise ValueError('List size too small')

    gains = []
    loses = []
    prices = []

    for candle in candles:
        prices.append(candle['close'])

    for n in range(0, len(prices) - 1):
        gain = prices[n + 1] - prices[n]
        if gain > 0:
            gains.append(gain)
        else:
            loses.append(-gain)

    avg_gain = sum(gains) / len(gains)
    avg_lose = sum(loses) / len(loses)
    rsi = 100.0 - 100.0 / (1.0 + avg_gain / avg_lose)
    return rsi


def get_hourly_close(timestamp: int, market) -> float:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        SELECT p.timestamp,
               m.market,
               p.close
          FROM market_hourly_prices p
          JOIN markets m
            ON m.id = p.market_id
         WHERE p.timestamp <= ?
           AND m.market = ?
      ORDER BY p.timestamp DESC
         LIMIT 1
    ''', (
        timestamp,
        market,
    ))
    result = cursor.fetchone()
    candle = {}
    candle['timestamp'] = result['timestamp']
    candle['market'] = result['market']
    candle['close'] = result['close']

    cursor.close()
    connection.commit()
    connection.close()
    return candle['close']


def get_hourly_candles(timestamp: int, market: str) -> list:
    candles = []
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        SELECT p.open,
               p.high,
               p.low,
               p.close,
               p.volume
          FROM market_hourly_prices p
          JOIN markets m
            ON m.id = p.market_id
         WHERE p.timestamp < ?
           AND m.market = ?
      ORDER BY p.timestamp DESC
         LIMIT 15
    ''', (
        timestamp,
        market,
    ))
    result = cursor.fetchall()
    for data in result[::-1]:
        candle = {}
        candle['timestamp'] = timestamp
        candle['market'] = market
        candle['open'] = data['open']
        candle['high'] = data['high']
        candle['low'] = data['low']
        candle['close'] = data['close']
        candle['volume'] = data['volume']
        candles.append(candle)
    cursor.close()
    connection.commit()
    connection.close()
    return candles


def simulate_hourly(market: str, cash: float) -> float:
    logger.debug(f'simulate() - Start')

    eur = cash
    fees = 0.0
    coins = 0.0
    price = 0.0

    start = int(datetime(2021, 1, 1, 00, 00, 00).timestamp())
    end = int(datetime(2021, 9, 26, 23, 00, 00).timestamp())
    hour = 3600

    for timestamp in range(start, end, hour):
        data = get_hourly_candles(timestamp, market)
        rsi = get_rsi(data)
        day = datetime.fromtimestamp(timestamp)

        # if day.day == 1 and day.hour == 10:
        #     eur += 100.0

        if rsi < 30.0 and eur > 0.0:
            price = get_hourly_close(timestamp, market)
            fee = 0.0025 * eur
            eur -= fee
            coins = eur / price
            fees += fee
            logger.info(f' Buy {coins:7.05f} for €{eur:7.02f}')
            eur = 0.0
            balance = eur + coins * price
            logger.info(f'{market} {day:%Y-%m-%d %H:%M} {rsi:5.1f} -  Buy: {coins:7.05f} + {eur:7.02f} = {balance:7.02f} ({fees:.02f})')
        elif rsi > 70.0 and coins > 0.0:
            price = get_hourly_close(timestamp, market)
            fee = 0.0025 * coins
            coins -= fee
            eur = price * coins
            fees += fee * price
            logger.info(f'Sell {coins:7.05f} for €{eur:7.02f}')
            coins = 0.0
            balance = eur + coins * price
            logger.info(f'{market} {day:%Y-%m-%d %H:%M} {rsi:5.1f} - Sell: {coins:7.05f} + {eur:7.02f} = {balance:7.02f} ({fees:.02f})')
            # time.sleep(1)
        else:
            price = get_hourly_close(timestamp, market)
            balance = eur + coins * price
            # logger.info(f'{market} {day:%Y-%m-%d %H:%M} {rsi:5.1f}         {coins:7.05f} / {eur:7.02f} = {balance:7.02f} / {fees:7.02f}')

    logger.debug(f'simulate() - Finish')
    return eur + coins * price


if __name__ == '__main__':
    try:
        logger.info(f'Start - {__file__}')

        markets = [
            'BTC-EUR',
            # 'ETH-EUR',
            # 'ADA-EUR',
            # 'XRP-EUR',
        ]
        balance = {}

        for market in markets:
            start = 100.0
            end = simulate_hourly(market, start)
            balance[market] = end - start

        for market in markets:
            logger.info(f'{market} {balance[market]:.02f}')

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
