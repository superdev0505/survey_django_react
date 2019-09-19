#!/usr/bin/env bash

#
# 1. mk file .pgpass which contains
#       localhost:5432:survey:survey:pass  <--------  DO not forget to change to real password
#
# 2. grant rights 600
#       chmod 600 .pgpass
#
# 3. put current script to cron
#       crontab -e
#
# ########################
#
# To restore backup locally:
#       pg_restore -U mingle_cash -d mingle_cash_db -v './2017-11-2.backup'
#
#

TODAY=$(date +%F)
cd /root/postgre_dump
pg_dump -U survey -h localhost -F c -b -v -f "./$TODAY.survey.backup" survey