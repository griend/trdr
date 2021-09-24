--
-- sqlite3 ~/var/trader/db/trader.db < btc.sql
--
SELECT   date(d.timestamp, 'unixepoch'),
         d.open,
         d.high,
         d.low,
         d.close,
         d.volume
FROM     markets m,
         market_daily_prices d
WHERE    m.market = 'BTC-EUR'
AND      m.id = d.market_id
ORDER BY d.timestamp;
