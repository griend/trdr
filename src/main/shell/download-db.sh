#!/bin/bash

set -e

BACKUP="trader-$(date +%Y%m%d).db"

cd ~/var/trader/db

sqlite3 trader.db ".backup ${BACKUP}"

sftp -P 3351 asrv0000019:var/trader/db/trader.db

rm -f $(ls -1r trader-????????.db | sed -ne '5,$p')
