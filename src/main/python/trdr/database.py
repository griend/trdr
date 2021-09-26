import logging
import sqlite3

from . import config

logger = logging.getLogger(__name__)


def create_db():
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS markets (
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
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_markets AFTER UPDATE ON markets
        BEGIN
            UPDATE markets
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  id = new.id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_updates (
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
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_market_updates AFTER UPDATE ON market_updates
        BEGIN
            UPDATE market_updates
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  id = new.id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_daily_prices (
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
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_market_daily_prices AFTER UPDATE ON market_daily_prices
        BEGIN
            UPDATE market_daily_prices
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  id = new.id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_hourly_prices (
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
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_market_hourly_prices AFTER UPDATE ON market_hourly_prices
        BEGIN
            UPDATE market_hourly_prices
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  id = new.id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candle1m (
            timestamp            INTEGER NOT NULL,
            market_id            INTEGER NOT NULL,
            open                 REAL NOT NULL,
            high                 REAL NOT NULL,
            low                  REAL NOT NULL,
            close                REAL NOT NULL,
            volume               REAL NOT NULL,
            created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            PRIMARY KEY (timestamp, market_id),
            FOREIGN KEY (market_id) REFERENCES markets (id) 
                ON DELETE CASCADE 
                ON UPDATE NO ACTION
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_candle1m AFTER UPDATE ON candle1m
        BEGIN
            UPDATE candle1m
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  timestamp = new.timestamp AND market_id = new.market_id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candle5m (
            timestamp            INTEGER NOT NULL,
            market_id            INTEGER NOT NULL,
            open                 REAL NOT NULL,
            high                 REAL NOT NULL,
            low                  REAL NOT NULL,
            close                REAL NOT NULL,
            volume               REAL NOT NULL,
            created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            PRIMARY KEY (timestamp, market_id),
            FOREIGN KEY (market_id) REFERENCES markets (id) 
                ON DELETE CASCADE 
                ON UPDATE NO ACTION
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_candle5m AFTER UPDATE ON candle5m
        BEGIN
            UPDATE candle5m
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  timestamp = new.timestamp AND market_id = new.market_id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candle1h (
            timestamp            INTEGER NOT NULL,
            market_id            INTEGER NOT NULL,
            open                 REAL NOT NULL,
            high                 REAL NOT NULL,
            low                  REAL NOT NULL,
            close                REAL NOT NULL,
            volume               REAL NOT NULL,
            created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            PRIMARY KEY (timestamp, market_id),
            FOREIGN KEY (market_id) REFERENCES markets (id) 
                ON DELETE CASCADE 
                ON UPDATE NO ACTION
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_candle1h AFTER UPDATE ON candle1h
        BEGIN
            UPDATE candle1h
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  timestamp = new.timestamp AND market_id = new.market_id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candle1d (
            timestamp            INTEGER NOT NULL,
            market_id            INTEGER NOT NULL,
            open                 REAL NOT NULL,
            high                 REAL NOT NULL,
            low                  REAL NOT NULL,
            close                REAL NOT NULL,
            volume               REAL NOT NULL,
            created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            PRIMARY KEY (timestamp, market_id),
            FOREIGN KEY (market_id) REFERENCES markets (id) 
                ON DELETE CASCADE 
                ON UPDATE NO ACTION
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_candle1d AFTER UPDATE ON candle1d
        BEGIN
            UPDATE candle1d
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  timestamp = new.timestamp AND market_id = new.market_id;
        END
    ''')

    connection.commit()
    connection.close()


def drop_db():
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute('DROP TABLE IF EXISTS candle1d')
    cursor.execute('DROP TABLE IF EXISTS candle1h')
    cursor.execute('DROP TABLE IF EXISTS candle5m')
    cursor.execute('DROP TABLE IF EXISTS candle1m')
    cursor.execute('DROP TABLE IF EXISTS market_hourly_prices')
    cursor.execute('DROP TABLE IF EXISTS market_daily_prices')
    cursor.execute('DROP TABLE IF EXISTS market_updates')
    cursor.execute('DROP TABLE IF EXISTS markets')

    connection.commit()
    connection.close()


if __name__ == '__main__':
    try:
        logger.info(f'Start - {__file__}')

        # drop_db()
        create_db()

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
