import logging
import sqlite3

from .. import config

logger = logging.getLogger(__name__)


def create_db():
    connection = sqlite3.connect(config['db_filename'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id                   INTEGER PRIMARY KEY,
            description          TEXT,
            created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_simulations AFTER UPDATE ON simulations
        BEGIN
            UPDATE simulations
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  id = new.id;
        END
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulate_trades (
            id                   INTEGER PRIMARY KEY,
            simulation_id        INTEGER NOT NULL,
            timestamp            INTEGER NOT NULL,
            market_id            INTEGER NOT NULL,
            eur_debet            FLOAT NOT NULL,
            eur_credit           FLOAT NOT NULL,
            eur_balance          FLOAT NOT NULL,
            coin_debet           FLOAT NOT NULL,
            coin_credit          FLOAT NOT NULL,
            coin_balance         FLOAT NOT NULL,
            fees                 FLOAT NOT NULL,
            price                FLOAT NOT NULL,
            created_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            updated_on           INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (simulation_id) REFERENCES simulations (id) 
                ON DELETE CASCADE 
                ON UPDATE NO ACTION,
            FOREIGN KEY (market_id) REFERENCES markets (id) 
                ON DELETE CASCADE 
                ON UPDATE NO ACTION
        )
    ''')

    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_simulate_trades AFTER UPDATE ON simulate_trades
        BEGIN
            UPDATE simulate_trades
            SET    updated_on = (strftime('%s', 'now'))
            WHERE  id = new.id;
        END
    ''')

    cursor.close()
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
