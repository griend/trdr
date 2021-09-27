import datetime
import logging
import sqlite3
from datetime import datetime
from enum import Enum

from .. import config


class Action(Enum):
    NOP = 0,
    BUY = 1,
    SELL = 2,


def create_simulation(description: str = "") -> int:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO simulations (
            description
        ) VALUES (?)''', (
        description,
    ))
    id = cursor.lastrowid
    cursor.close()
    connection.commit()
    connection.close()

    return id


def create_simulate_trade(simulation_id: int,
                          timestamp: int,
                          market_id: int,
                          eur_debet: float,
                          eur_credit: float,
                          eur_balance: float,
                          coin_debet: float,
                          coin_credit: float,
                          coin_balance: float,
                          fees: float,
                          price: float) -> None:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO simulate_trades (
            simulation_id,
            timestamp,
            market_id,
            eur_debet,
            eur_credit,
            eur_balance,
            coin_debet,
            coin_credit,
            coin_balance,
            fees,
            price
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        simulation_id,
        timestamp,
        market_id,
        eur_debet,
        eur_credit,
        eur_balance,
        coin_debet,
        coin_credit,
        coin_balance,
        fees,
        price
    ))
    cursor.close()
    connection.commit()
    connection.close()


def simulate_buy(simulation_id: int,
                 timestamp: int,
                 market_id: int,
                 eur_credit: float,
                 eur_balance: float,
                 coin_debet: float,
                 coin_balance: float,
                 fees: float,
                 price: float) -> None:
    create_simulate_trade(simulation_id,
                          timestamp,
                          market_id,
                          0.0,
                          eur_credit,
                          eur_balance,
                          coin_debet,
                          0.0,
                          coin_balance,
                          fees,
                          price)


def simulate_sell(simulation_id: int,
                  timestamp: int,
                  market_id: int,
                  eur_debet: float,
                  eur_balance: float,
                  coin_credit: float,
                  coin_balance: float,
                  fees: float,
                  price: float) -> None:
    create_simulate_trade(simulation_id,
                          timestamp,
                          market_id,
                          eur_debet,
                          0.0,
                          eur_balance,
                          0.0,
                          coin_credit,
                          coin_balance,
                          fees,
                          price)


def __get_closes(timestamp: int, market_id: int) -> list:
    closes = []
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        SELECT p.close
          FROM market_hourly_prices p
         WHERE p.timestamp < ?
           AND p.market_id = ?
      ORDER BY p.timestamp DESC
         LIMIT 15
    ''', (
        timestamp,
        market_id,
    ))
    result = cursor.fetchall()
    for data in result[::-1]:
        closes.append(data['close'])
    cursor.close()
    connection.commit()
    connection.close()
    return closes


def get_rsi(timestamp: int, market_id: int) -> float:
    closes = __get_closes(timestamp, market_id)

    gains = []
    loses = []
    prices = []

    for n in range(0, len(closes) - 1):
        gain = closes[n + 1] - closes[n]
        if gain > 0:
            gains.append(gain)
        else:
            loses.append(-gain)

    avg_gain = sum(gains) / len(gains)
    avg_lose = sum(loses) / len(loses)
    rsi = 100.0 - 100.0 / (1.0 + avg_gain / avg_lose)
    return rsi


def analyse(timestamp: int, market_id: int, eur_balance: float, coin_balance: float) -> Action:
    rsi = get_rsi(timestamp, market_id)

    if rsi < 30.0 and eur_balance > 0.0:
        action = Action.BUY
    elif rsi > 70.0 and coin_balance > 0.0:
        action = Action.SELL
    else:
        action = Action.NOP

    return action


def get_price(timestamp: int, market_id: int) -> float:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        SELECT p.close
          FROM market_hourly_prices p
         WHERE p.timestamp <= ?
           AND p.market_id = ?
      ORDER BY p.timestamp DESC
         LIMIT 1
    ''', (
        timestamp,
        market_id,
    ))
    result = cursor.fetchone()
    price = result['close']

    cursor.close()
    connection.commit()
    connection.close()
    return price


def get_market_id(market: str) -> int:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        SELECT m.id
          FROM markets m
         WHERE m.market = ?
    ''', (
        market,
    ))
    result = cursor.fetchone()
    market_id = result['id']

    cursor.close()
    connection.commit()
    connection.close()
    return market_id


def trade(simulation_id: int, timestamp: int, market_id: int, eur_balance: float, coin_balance: float) -> (float, float):
    action = analyse(timestamp, market_id, eur_balance, coin_balance)
    if action == Action.BUY:
        price = get_price(timestamp, market_id)
        fee = eur_balance * 0.0025
        eur_balance -= fee
        coin_debet = eur_balance / price
        coin_balance = coin_debet
        eur_credit = eur_balance
        eur_balance = 0.0
        simulate_buy(simulation_id,
                     timestamp,
                     market_id,
                     eur_credit,
                     eur_balance,
                     coin_balance,
                     coin_balance,
                     fee,
                     price)
        dt = datetime.fromtimestamp(timestamp)
        logger.info(f'{dt:%Y-%m-%d %H:%M}  Buy {coin_debet:7.05f} for €{eur_credit:7.02f} (€{fee:.2f})')
        return (eur_balance, coin_balance)
    elif action == Action.SELL:
        price = get_price(timestamp, market_id)
        eur_debet = coin_balance * price
        fee = eur_debet * 0.0025
        eur_debet -= fee
        eur_balance = eur_debet
        coin_credit = coin_balance
        coin_balance = 0.0
        simulate_sell(simulation_id,
                      timestamp,
                      market_id,
                      eur_debet,
                      eur_balance,
                      coin_credit,
                      coin_balance,
                      fee,
                      price)
        dt = datetime.fromtimestamp(timestamp)
        logger.info(f'{dt:%Y-%m-%d %H:%M} Sell {coin_credit:7.05f} for €{eur_debet:7.02f} (€{fee:.2f})')
        return (eur_balance, coin_balance)
    else:
        return (eur_balance, coin_balance)


def simulate(market: str, balance: float, description: str = ""):
    simulation_id = create_simulation(description)
    market_id = get_market_id(market)

    start = int(datetime(2021, 1, 1, 00, 00, 00).timestamp())
    end = int(datetime(2021, 9, 26, 23, 00, 00).timestamp())
    hour = 3600
    eur_balance = balance
    coin_balance = 0.0

    for timestamp in range(start, end, hour):
        eur_balance, coin_balance = trade(simulation_id, timestamp, market_id, eur_balance, coin_balance)


logger = logging.getLogger(__name__)
if __name__ == '__main__':
    try:
        logger.info(f'Start - {__file__}')

        simulate('BTC-EUR', 100.0, 'A test run with €100')

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
