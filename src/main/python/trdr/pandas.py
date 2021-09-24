import sqlite3

import pandas as pd
import matplotlib.pyplot as plt

from . import config


def demo() -> None:
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row

    df = pd.read_sql_query('''
        SELECT  d.timestamp AS date,
                d.open AS open,
                d.high AS high,
                d.low AS low,
                d.close AS close
        FROM    market_daily_prices d
        JOIN    markets m
        ON      m.id = d.market_id
        WHERE   m.market = 'BTC-EUR'
    ''', connection, index_col='date', parse_dates={'date': 's'})

    connection.close()

    # btc = df.loc['2020-01-01':]
    # btc.plot()
    df.plot()

    plt.title('BTC-EUR')
    plt.show()


if __name__ == '__main__':
    demo()
