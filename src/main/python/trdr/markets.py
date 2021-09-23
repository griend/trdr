import logging
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from python_bitvavo_api.bitvavo import Bitvavo

from . import config
from .hostname import get_hostname, get_public_address
from .trader import connect

logger = logging.getLogger(__name__)


def to_datetime(time: int) -> datetime:
    timezone = ZoneInfo('Europe/Amsterdam')
    dt = datetime.fromtimestamp(time / 1000, timezone)

    return dt


def connect_db(config: hash):
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
            created_on           TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_on           TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_markets AFTER UPDATE ON markets
        BEGIN
            UPDATE markets
            SET    updated_on = (datetime('now', 'localtime'))
            WHERE  id = new.id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_updates (
            id                   INTEGER PRIMARY KEY,
            market_id            INTEGER NOT NULL,
            type                 TEXT NOT NULL,
            status               TEXT NOT NULL,
            timestamp_start      TEXT NOT NULL,
            timestamp_end        TEXT NOT NULL,
            timestamp_update     TEXT NOT NULL,
            created_on           TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_on           TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (market_id) REFERENCES markets (id) 
                ON DELETE CASCADE 
            ON UPDATE NO ACTION
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_market_updates AFTER UPDATE ON market_updates
        BEGIN
            UPDATE market_updates
            SET    updated_on = (datetime('now', 'localtime'))
            WHERE  id = new.id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_daily_prices (
            id                   INTEGER PRIMARY KEY,
            market_id            INTEGER NOT NULL,
            timestamp            TEXT NOT NULL,
            open                 REAL NOT NULL,
            high                 REAL NOT NULL,
            low                  REAL NOT NULL,
            close                REAL NOT NULL,
            volume               REAL NOT NULL,
            created_on           TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_on           TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (market_id) REFERENCES markets (id) 
                ON DELETE CASCADE 
                ON UPDATE NO ACTION
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_market_daily_prices AFTER UPDATE ON market_daily_prices
        BEGIN
            UPDATE market_daily_prices
            SET    updated_on = (datetime('now', 'localtime'))
            WHERE  id = new.id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_hourly_prices (
            id                   INTEGER PRIMARY KEY,
            market_id            INTEGER NOT NULL,
            timestamp            TEXT NOT NULL,
            open                 REAL NOT NULL,
            high                 REAL NOT NULL,
            low                  REAL NOT NULL,
            close                REAL NOT NULL,
            volume               REAL NOT NULL,
            created_on           TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_on           TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (market_id) REFERENCES markets (id) 
                ON DELETE CASCADE 
                ON UPDATE NO ACTION
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_market_hourly_prices AFTER UPDATE ON market_hourly_prices
        BEGIN
            UPDATE market_hourly_prices
            SET    updated_on = (datetime('now', 'localtime'))
            WHERE  id = new.id;
        END
    ''')

    return connection


def get_markets(bitvavo: Bitvavo) -> None:
    logger.debug('get_markets() - Start')

    connection = connect_db(config)
    cursor = connection.cursor()
    rows = cursor.execute('SELECT * FROM markets')
    markets = [row['market'] for row in rows]

    response = bitvavo.markets({})
    for market in response:
        if market['market'] not in markets:
            cursor.execute('''
                INSERT INTO markets (
                    market, 
                    status, 
                    base, 
                    quote, 
                    pricePrecision, 
                    minOrderInQuoteAsset, 
                    minOrderInBaseAsset, 
                    orderTypes
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                market['market'],
                market['status'],
                market['base'],
                market['quote'],
                int(market['pricePrecision']),
                float(market['minOrderInQuoteAsset']),
                float(market['minOrderInBaseAsset']),
                ', '.join(market['orderTypes'])))
            logger.info(f"Inserted: {market['market']}")
        else:
            cursor.execute('''
                UPDATE markets 
                SET    status = ?, 
                       base = ?, 
                       quote = ?, 
                       pricePrecision = ?, 
                       minOrderInQuoteAsset = ?, 
                       minOrderInBaseAsset = ?, 
                       orderTypes = ?
                WHERE  market = ?
            ''', (
                market['status'],
                market['base'],
                market['quote'],
                int(market['pricePrecision']),
                float(market['minOrderInQuoteAsset']),
                float(market['minOrderInBaseAsset']),
                ', '.join(market['orderTypes']),
                market['market']
            ))
            logger.info(f"Updated: {market['market']}")

    connection.commit()
    connection.close()

    logger.debug('get_markets() - Finish')


def set_market_updates():
    logger.debug('get_daily_prices() - Start')

    start_dt = datetime(2020, 1, 1)
    end_dt = datetime(2041, 1, 1)

    connection = connect_db(config)
    cursor0 = connection.cursor()
    rows0 = cursor0.execute('''
        SELECT * 
        FROM   markets 
        WHERE  status = 'trading'
    ''')

    for row0 in rows0:
        market_id = row0['id']

        cursor1 = connection.cursor()
        cursor1.execute('''
            INSERT INTO market_updates (
                market_id,
                type,
                status,
                timestamp_start,
                timestamp_end,
                timestamp_update
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            market_id,
            'daily',
            'active',
            start_dt,
            end_dt,
            start_dt))
        cursor1.execute('''
            INSERT INTO market_updates (
                market_id,
                type,
                status,
                timestamp_start,
                timestamp_end,
                timestamp_update
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            market_id,
            'hourly',
            'active',
            start_dt,
            end_dt,
            start_dt))

    connection.commit()
    connection.close()

    logger.debug('get_markets() - Finish')


def get_daily_prices(bitvavo: Bitvavo) -> None:
    logger.debug('get_daily_prices() - Start')

    connection = connect_db(config)
    cursor0 = connection.cursor()
    result0 = cursor0.execute('''
        SELECT * 
        FROM   markets 
        WHERE  status = 'trading'
    ''')

    for row0 in result0:
        market_id = row0['id']
        market = row0['market']

        cursor1 = connection.cursor()
        result1 = cursor1.execute('''
            SELECT *
            FROM   market_updates
            WHERE  market_id = ?
            AND    type = 'daily'
            AND    status = 'active'
            AND    timestamp_start <= date('now')
            AND    timestamp_end > date('now')
        ''', (
            market_id,
        ))

        row1 = result1.fetchone()
        update_id = int(row1['id'])
        now_dt = datetime.now()
        start_dt = datetime.fromisoformat(row1['timestamp_update'])

        if start_dt > now_dt:
            start_dt = now_dt

        end_dt = start_dt + timedelta(days=60)

        if end_dt > now_dt:
            end_dt = now_dt

        start_ms = int(start_dt.timestamp() * 1000)
        end_ms = int(end_dt.timestamp() * 1000)

        response = bitvavo.candles(market, '1d', {'start': start_ms, 'end': end_ms})

        for candle in response[::-1]:
            timestamp = to_datetime(candle[0])
            open = float(candle[1])
            high = float(candle[2])
            low = float(candle[3])
            close = float(candle[4])
            volume = float(candle[5])

            cursor2 = connection.cursor()
            result2 = cursor2.execute('''
                SELECT id
                FROM   market_daily_prices
                WHERE  market_id = ?
                AND    timestamp = ?
            ''', (
                market_id,
                timestamp,
            ))

            row2 = result2.fetchone()

            if row2:
                id = int(row2['id'])
                cursor3 = connection.cursor()
                cursor3.execute('''
                    UPDATE  market_daily_prices
                    SET     market_id = ?, 
                            timestamp = ?,
                            open = ?, 
                            high = ?, 
                            low = ?, 
                            close = ?, 
                            volume = ?
                    WHERE   id = ?
                ''', (
                    market_id,
                    timestamp,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    id
                ))
                logger.info(f'Update: {market_id} ({market}), {timestamp:%Y-%m-%d}')
            else:
                cursor4 = connection.cursor()
                cursor4.execute('''
                    INSERT INTO market_daily_prices (
                        market_id, 
                        timestamp,
                        open, 
                        high, 
                        low, 
                        close, 
                        volume
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                    market_id,
                    timestamp,
                    open,
                    high,
                    low,
                    close,
                    volume
                ))
                logger.info(f'Insert: {market_id} ({market}), {timestamp:%Y-%m-%d}')

        cursor5 = connection.cursor()
        cursor5.execute('''
            UPDATE market_updates
            SET    timestamp_update = ?
            WHERE  id = ?
        ''', (
            end_dt,
            update_id,
        ))

        logger.info(f'Updated daily prices: {market} ({start_dt:%Y-%m-%d})')

    connection.commit()
    connection.close()

    logger.debug('get_daily_prices() - Finish')


def get_hourly_prices(bitvavo: Bitvavo) -> None:
    logger.debug('get_hourly_prices() - Start')

    connetion = connect_db(config)
    cursor0 = connetion.cursor()
    rows0 = cursor0.execute('''
        SELECT * 
        FROM   markets 
        WHERE  status = 'trading'
    ''')

    for row0 in rows0:
        market_id = row0['id']
        market = row0['market']

        cursor1 = connetion.cursor()
        rows1 = cursor1.execute('''
            SELECT *
            FROM   market_updates
            WHERE  market_id = ?
            AND    type = 'hourly'
            AND    status = 'active'
            AND    timestamp_start <= date('now')
            AND    timestamp_end > date('now')
        ''', (
            market_id,
        ))

        row1 = rows1.fetchone()
        update_id = int(row1['id'])
        start_dt = datetime.fromisoformat(row1['timestamp_update'])
        end_dt = start_dt + timedelta(days=14)
        start_ms = int(start_dt.timestamp() * 1000)
        end_ms = int(end_dt.timestamp() * 1000)

        response = bitvavo.candles(market, '1h', {'start': start_ms, 'end': end_ms})

        for candle in response[::-1]:
            timestamp = to_datetime(candle[0])
            open = float(candle[1])
            high = float(candle[2])
            low = float(candle[3])
            close = float(candle[4])
            volume = float(candle[5])

            cursor2 = connetion.cursor()
            cursor2.execute('''
                DELETE FROM market_hourly_prices
                WHERE  market_id = ?
                AND    timestamp = ?
            ''', (
                market_id,
                timestamp,
            ))
            cursor2.execute('''
                INSERT INTO market_hourly_prices (
                    market_id, 
                    timestamp, 
                    open, 
                    high, 
                    low, 
                    close, 
                    volume
                ) VALUES(?, ?, ?, ?, ?, ?, ?)
            ''', (
                market_id,
                timestamp,
                open,
                high,
                low,
                close,
                volume
            ))

            logger.info(f'Update: {market_id} ({market}), {timestamp:%Y-%m-%d %H:%M}')

            cursor2.execute('''
                UPDATE market_updates
                SET    timestamp_update = ?
                WHERE  id = ?
            ''', (
                timestamp,
                update_id,
            ))

        logger.info(f'Updated hourly prices: {market} ({start_dt:%Y-%m-%d %H:%M})')

    connetion.commit()
    connetion.close()

    logger.debug('get_hourly_prices() - Finish')


if __name__ == '__main__':
    try:
        logger.info(f'Start - {__file__}')
        address = get_public_address()
        hostname = get_hostname(address)
        logger.info(f'Hostname: {hostname} ({address})')

        bitvavo = connect(config)
        # get_markets(bitvavo)
        # set_market_updates()

        get_daily_prices(bitvavo)
        # get_hourly_prices(bitvavo)

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
