import logging
import sqlite3
from datetime import datetime
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


def populate_markets(bitvavo: Bitvavo) -> None:
    logger.debug('populate_markets() - Start')
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        SELECT   * 
        FROM     markets
        ORDER BY market
    ''')
    markets = cursor.fetchall()
    cache = [market['market'] for market in markets]
    response = bitvavo.markets({})

    for market in response:
        if market['market'] not in cache:
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
                ', '.join(market['orderTypes'])
            ))
            logger.info(f"Inserted: {market['market']}")
        else:
            cursor.execute('''
                SELECT * 
                FROM   markets
                WHERE  market = ?
            ''', (
                market['market'],
            ))
            current = cursor.fetchone()

            if market['market'] != current['market']:
                logger.info(f"Market: {market['market']}")
                updated = True
            elif market['status'] != current['status']:
                logger.info(f"Status: {market['status']}")
                updated = True
            elif market['base'] != current['base']:
                logger.info(f"Base: {market['base']}")
                updated = True
            elif market['quote'] != current['quote']:
                logger.info(f"Quote: {market['quote']}")
                updated = True
            elif int(market['pricePrecision']) != current['pricePrecision']:
                logger.info(f"pricePrecision: {market['pricePrecision']}")
                updated = True
            elif float(market['minOrderInQuoteAsset']) != current['minOrderInQuoteAsset']:
                logger.info(f"minOrderInQuoteAsset: {market['minOrderInQuoteAsset']}")
                updated = True
            elif float(market['minOrderInBaseAsset']) != current['minOrderInBaseAsset']:
                logger.info(f"minOrderInBaseAsset: {market['minOrderInBaseAsset']}")
                updated = True
            elif ', '.join(market['orderTypes']) != current['orderTypes']:
                logger.info(f"orderTypes: {', '.join(market['orderTypes'])}")
                updated = True
            else:
                updated = False

            if updated:
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

    logger.debug('populate_markets() - Finish')


def populate_market_updates() -> None:
    logger.debug('populate_market_updates() - Start')
    start_epoch = int(datetime(2019, 1, 1).timestamp())
    end_epoch = int(datetime(2061, 1, 1).timestamp())
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        SELECT   * 
        FROM     markets 
        WHERE    status = 'trading'
        ORDER BY market
    ''')
    markets = cursor.fetchall()

    for market in markets:
        market_id = market['id']
        cursor.execute('''
            SELECT COUNT(*) AS cnt
            FROM   market_updates
            WHERE  market_id = ?
            AND    type = 'daily'
        ''', (
            market_id,
        ))
        count = cursor.fetchone()['cnt']

        if count == 0:
            cursor.execute('''
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
                start_epoch,
                end_epoch,
                start_epoch
            ))
            logger.info(f'Inserted market_updates: {market["market"]} / daily')

        cursor.execute('''
            SELECT COUNT(*) AS cnt
            FROM   market_updates
            WHERE  market_id = ?
            AND    type = 'hourly'
        ''', (
            market_id,
        ))
        count = cursor.fetchone()['cnt']

        if count == 0:
            cursor.execute('''
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
                start_epoch,
                end_epoch,
                start_epoch
            ))
            logger.info(f'Inserted market_updates: {market["market"]} / hourly')

    connection.commit()
    connection.close()

    logger.debug('populate_market_updates() - Finish')


def populate_daily_prices(bitvavo: Bitvavo) -> None:
    logger.debug('populate_daily_prices() - Start')
    # 60 days of 24 hours in seconds
    interval = 60 * 24 * 60 * 60
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        SELECT   * 
        FROM     markets 
        WHERE    status = 'trading'
        ORDER BY market
    ''')
    markets = cursor.fetchall()
    now_epoch = int(datetime.now().timestamp())

    for market in markets:
        market_id = market['id']
        market = market['market']
        cursor.execute('''
            SELECT *
            FROM   market_updates
            WHERE  market_id = ?
            AND    type = 'daily'
            AND    status = 'active'
            AND    timestamp_start <= ?
            AND    timestamp_end > ?
        ''', (
            market_id,
            now_epoch,
            now_epoch
        ))

        update = cursor.fetchone()
        update_id = int(update['id'])
        start_epoch = update['timestamp_update']

        if start_epoch > now_epoch:
            start_epoch = now_epoch

        end_epoch = start_epoch + interval

        if end_epoch > now_epoch:
            end_epoch = now_epoch

        update_epoch = end_epoch

        start_ms = start_epoch * 1000
        end_ms = end_epoch * 1000

        response = bitvavo.candles(market, '1d', {'start': start_ms, 'end': end_ms})

        for candle in response[::-1]:
            timestamp = int(to_datetime(candle[0]).timestamp())
            open = float(candle[1])
            high = float(candle[2])
            low = float(candle[3])
            close = float(candle[4])
            volume = float(candle[5])

            cursor.execute('''
                SELECT id
                FROM   market_daily_prices
                WHERE  market_id = ?
                AND    timestamp = ?
            ''', (
                market_id,
                timestamp,
            ))
            current = cursor.fetchone()

            if current:
                id = int(current['id'])
                cursor.execute('''
                    SELECT  *
                    FROM    market_daily_prices
                    WHERE   id == ?
                ''', (
                    id,
                ))
                old = cursor.fetchone()

                if market_id != old['market_id']:
                    updated = True
                elif timestamp != old['timestamp']:
                    updated = True
                elif timestamp != old['timestamp']:
                    updated = True
                elif open != old['open']:
                    updated = True
                elif high != old['high']:
                    updated = True
                elif low != old['low']:
                    updated = True
                elif close != old['close']:
                    updated = True
                elif volume != old['volume']:
                    updated = True
                else:
                    updated = False

                if updated:
                    cursor.execute('''
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
                    dt = datetime.fromtimestamp(timestamp)
                    logger.info(f'Update: {market_id} ({market}), {dt}')
            else:
                cursor.execute('''
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
                dt = datetime.fromtimestamp(timestamp)
                logger.info(f'Insert: {market_id} ({market}), {dt}')

            update_epoch = timestamp

        cursor.execute('''
            UPDATE market_updates
            SET    timestamp_update = ?
            WHERE  id = ?
        ''', (
            update_epoch,
            update_id,
        ))

        dt = datetime.fromtimestamp(start_epoch)
        logger.info(f'Updated daily prices: {market} ({dt})')

    connection.commit()
    connection.close()

    logger.debug('populate_daily_prices() - Finish')


def populate_hourly_prices(bitvavo: Bitvavo) -> None:
    logger.debug('populate_hourly_prices() - Start')
    # 15 days of 24 hours in seconds
    interval = 15 * 24 * 60 * 60
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('''
        SELECT   * 
        FROM     markets 
        WHERE    status = 'trading'
        ORDER BY market
    ''')
    markets = cursor.fetchall()
    now_epoch = int(datetime.now().timestamp())

    for market in markets:
        market_id = market['id']
        market = market['market']
        cursor.execute('''
            SELECT *
            FROM   market_updates
            WHERE  market_id = ?
            AND    type = 'hourly'
            AND    status = 'active'
            AND    timestamp_start <= ?
            AND    timestamp_end > ?
        ''', (
            market_id,
            now_epoch,
            now_epoch
        ))

        update = cursor.fetchone()
        update_id = int(update['id'])
        start_epoch = update['timestamp_update']

        if start_epoch > now_epoch:
            start_epoch = now_epoch

        end_epoch = start_epoch + interval

        if end_epoch > now_epoch:
            end_epoch = now_epoch

        update_epoch = end_epoch

        start_ms = start_epoch * 1000
        end_ms = end_epoch * 1000

        response = bitvavo.candles(market, '1h', {'start': start_ms, 'end': end_ms})

        for candle in response[::-1]:
            timestamp = int(to_datetime(candle[0]).timestamp())
            open = float(candle[1])
            high = float(candle[2])
            low = float(candle[3])
            close = float(candle[4])
            volume = float(candle[5])

            cursor.execute('''
                SELECT id
                FROM   market_hourly_prices
                WHERE  market_id = ?
                AND    timestamp = ?
            ''', (
                market_id,
                timestamp,
            ))
            current = cursor.fetchone()

            if current:
                id = int(current['id'])
                cursor.execute('''
                    SELECT  *
                    FROM    market_hourly_prices
                    WHERE   id == ?
                ''', (
                    id,
                ))
                old = cursor.fetchone()

                if market_id != old['market_id']:
                    updated = True
                elif timestamp != old['timestamp']:
                    updated = True
                elif timestamp != old['timestamp']:
                    updated = True
                elif open != old['open']:
                    updated = True
                elif high != old['high']:
                    updated = True
                elif low != old['low']:
                    updated = True
                elif close != old['close']:
                    updated = True
                elif volume != old['volume']:
                    updated = True
                else:
                    updated = False

                if updated:
                    cursor.execute('''
                        UPDATE  market_hourly_prices
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
                    dt = datetime.fromtimestamp(timestamp)
                    logger.info(f'Update: {market_id} ({market}), {dt}')
            else:
                cursor.execute('''
                    INSERT INTO market_hourly_prices (
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
                dt = datetime.fromtimestamp(timestamp)
                logger.info(f'Insert: {market_id} ({market}), {dt}')

            update_epoch = timestamp

        cursor.execute('''
            UPDATE market_updates
            SET    timestamp_update = ?
            WHERE  id = ?
        ''', (
            update_epoch,
            update_id,
        ))

        dt = datetime.fromtimestamp(start_epoch)
        logger.info(f'Updated hourly prices: {market} ({dt})')

    connection.commit()
    connection.close()

    logger.debug('populate_hourly_prices() - Finish')


if __name__ == '__main__':
    try:
        logger.info(f'Start - {__file__}')
        address = get_public_address()
        logger.info(f'Hostname: {address}')

        bitvavo = connect(config)
        populate_markets(bitvavo)
        populate_market_updates()
        populate_daily_prices(bitvavo)
        populate_hourly_prices(bitvavo)

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
