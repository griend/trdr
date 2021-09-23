--
-- sqlite3 ~/var/trader/db/trader.db < btc_close.sq
--
SELECT   date(d.timestamp),
         m.market,
         d.close
FROM     markets m,
         market_daily_prices d
WHERE    m.market = 'BTC-EUR'
AND      m.id = d.market_id
ORDER BY d.timestamp;
