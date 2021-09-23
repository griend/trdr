import logging
import socket

import requests

logger = logging.getLogger(__name__)


def get_public_address() -> str:
    response = requests.get('http://ifconfig.io/ip')
    return response.text.strip()


def get_hostname(address) -> str:
    return socket.gethostbyaddr(address)[0]


if __name__ == '__main__':
    try:
        logger.info(f'Start - {__file__}')

        address = get_public_address()
        hostname = get_hostname(address)

        logger.info(f'Public IP: {address}')
        logger.info(f'Hostname: {hostname}')

        logger.info(f'Finish - {__file__}')
    except Exception as e:
        logger.fatal(e, exc_info=True)
