import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from .. import config

connection = sqlite3.connect(config['db_filename'])
connection.row_factory = sqlite3.Row

df = pd.read_sql_query('''
select p.timestamp,
       s.eur_debet,
       s.eur_credit,
       s.eur_balance,
       s.coin_debet,
       s.coin_credit,
       s.coin_balance
from   market_hourly_prices p
left outer join simulate_trades s
     on p.market_id = s.market_id and p.timestamp = s.timestamp and s.simulation_id = 11
where  p.market_id = 35;
''', connection, index_col='timestamp', parse_dates={'timestamp': 's'})

df = df.fillna(0.0)

df = df.loc['2021']
df = df.drop(columns=['eur_debet', 'eur_credit', 'coin_debet', 'coin_credit', 'coin_balance'])

print(df)

df.plot()
plt.show()