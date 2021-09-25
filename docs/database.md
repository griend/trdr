# Database

## markets


```bash
sqlite3 /Users/cees/var/trader/db/trader.db '.schema markets'
```

    CREATE TABLE markets (
                id                   INTEGER PRIMARY KEY,
                market               TEXT UNIQUE NOT NULL,
                status               TEXT NOT NULL,
                base                 TEXT NOT NULL,
                quote                TEXT NOT NULL,
                pricePrecision       INTEGER NOT NULL,
                minOrderInQuoteAsset REAL NOT NULL,
                minOrderInBaseAsset  REAL NOT NULL,
                orderTypes           TEXT NOT NULL,
                created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
            );
    CREATE TRIGGER trg_markets AFTER UPDATE ON markets
            BEGIN
                UPDATE markets
                SET    updated_on = (strftime('%s', 'now'))
                WHERE  id = new.id;
            END;



```bash
sqlite3 /Users/cees/var/trader/db/trader.db 'SELECT * FROM markets LIMIT 5' 
```

    1|1INCH-EUR|trading|1INCH|EUR|5|5.0|2.0|market, limit, stopLoss, stopLossLimit, takeProfit, takeProfitLimit|1632469889|1632469889
    2|AAVE-EUR|trading|AAVE|EUR|5|5.0|0.008|market, limit, stopLoss, stopLossLimit, takeProfit, takeProfitLimit|1632469889|1632469889
    3|ADA-BTC|halted|ADA|BTC|5|0.001|10.0|market, limit, stopLoss, stopLossLimit, takeProfit, takeProfitLimit|1632469889|1632469889
    4|ADA-EUR|trading|ADA|EUR|5|5.0|3.0|market, limit, stopLoss, stopLossLimit, takeProfit, takeProfitLimit|1632469889|1632469889
    5|ADX-EUR|trading|ADX|EUR|5|5.0|10.0|market, limit, stopLoss, stopLossLimit, takeProfit, takeProfitLimit|1632469889|1632469889


## market_updates


```bash
sqlite3 /Users/cees/var/trader/db/trader.db '.schema market_updates'
```

    CREATE TABLE market_updates (
                id                   INTEGER PRIMARY KEY,
                market_id            INTEGER NOT NULL,
                type                 TEXT NOT NULL,
                status               TEXT NOT NULL,
                timestamp_start      INTEGER NOT NULL,
                timestamp_end        INTEGER NOT NULL,
                timestamp_update     INTEGER NOT NULL,
                created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (market_id) REFERENCES markets (id) 
                    ON DELETE CASCADE 
                ON UPDATE NO ACTION
            );
    CREATE TRIGGER trg_market_updates AFTER UPDATE ON market_updates
            BEGIN
                UPDATE market_updates
                SET    updated_on = (strftime('%s', 'now'))
                WHERE  id = new.id;
            END;



```bash
sqlite3 /Users/cees/var/trader/db/trader.db 'SELECT * FROM market_updates LIMIT 5' 
```

    1|1|daily|active|1546297200|2871759600|1632528000|1632471594|1632566466
    2|1|hourly|active|1546297200|2871759600|1632564000|1632471594|1632566498
    3|2|daily|active|1546297200|2871759600|1632528000|1632471594|1632566466
    4|2|hourly|active|1546297200|2871759600|1632564000|1632471594|1632566510
    5|4|daily|active|1546297200|2871759600|1632528000|1632471594|1632566466


## market_daily_prices


```bash
sqlite3 /Users/cees/var/trader/db/trader.db '.schema market_daily_prices'
```

    CREATE TABLE market_daily_prices (
                id                   INTEGER PRIMARY KEY,
                market_id            INTEGER NOT NULL,
                timestamp            INTEGER NOT NULL,
                open                 REAL NOT NULL,
                high                 REAL NOT NULL,
                low                  REAL NOT NULL,
                close                REAL NOT NULL,
                volume               REAL NOT NULL,
                created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (market_id) REFERENCES markets (id) 
                    ON DELETE CASCADE 
                    ON UPDATE NO ACTION
            );
    CREATE TRIGGER trg_market_daily_prices AFTER UPDATE ON market_daily_prices
            BEGIN
                UPDATE market_daily_prices
                SET    updated_on = (strftime('%s', 'now'))
                WHERE  id = new.id;
            END;



```bash
sqlite3 /Users/cees/var/trader/db/trader.db 'SELECT * FROM market_daily_prices LIMIT 5' 
```

    1|4|1552003200|0.037966|0.038705|0.037424|0.037471|475011.225064|1632472994|1632472994
    2|4|1552089600|0.037594|0.04178|0.037594|0.041619|611702.353506|1632472994|1632472994
    3|4|1552176000|0.041105|0.041105|0.039581|0.040301|695109.33592|1632472994|1632472994
    4|4|1552262400|0.040529|0.042898|0.039665|0.0425|572567.041479|1632472994|1632472994
    5|4|1552348800|0.041773|0.042485|0.040057|0.041742|576629.590738|1632472994|1632472994


## market_hourly_prices


```bash
sqlite3 /Users/cees/var/trader/db/trader.db '.schema market_hourly_prices'
```

    CREATE TABLE market_hourly_prices (
                id                   INTEGER PRIMARY KEY,
                market_id            INTEGER NOT NULL,
                timestamp            INTEGER NOT NULL,
                open                 REAL NOT NULL,
                high                 REAL NOT NULL,
                low                  REAL NOT NULL,
                close                REAL NOT NULL,
                volume               REAL NOT NULL,
                created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (market_id) REFERENCES markets (id) 
                    ON DELETE CASCADE 
                    ON UPDATE NO ACTION
            );
    CREATE TRIGGER trg_market_hourly_prices AFTER UPDATE ON market_hourly_prices
            BEGIN
                UPDATE market_hourly_prices
                SET    updated_on = (strftime('%s', 'now'))
                WHERE  id = new.id;
            END;



```bash
sqlite3 /Users/cees/var/trader/db/trader.db 'SELECT * FROM market_daily_prices LIMIT 5' 
```

    1|4|1552003200|0.037966|0.038705|0.037424|0.037471|475011.225064|1632472994|1632472994
    2|4|1552089600|0.037594|0.04178|0.037594|0.041619|611702.353506|1632472994|1632472994
    3|4|1552176000|0.041105|0.041105|0.039581|0.040301|695109.33592|1632472994|1632472994
    4|4|1552262400|0.040529|0.042898|0.039665|0.0425|572567.041479|1632472994|1632472994
    5|4|1552348800|0.041773|0.042485|0.040057|0.041742|576629.590738|1632472994|1632472994

