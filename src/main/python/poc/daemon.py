'''
A Python daemon.

Listens for a SIGHUP signal.
'''
import logging
import os
import signal
import time

logger = logging.getLogger(__name__)
running = True


def handler(signum, frame):
    global running

    logger.debug(f'handler() - Start')

    running = False
    logger.info(f'Stopping...')

    logger.debug(f'handler() - Fininsh')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    try:
        logger.info(f'Start - {__file__}')
        logger.info(f'PID: {os.getpid()}')

        signal.signal(signal.SIGHUP, handler)

        while running:
            logger.info('Sleeping...')
            time.sleep(1)

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
