#!/usr/bin/env bash

cd /var/www/survey
date > /var/www/tmp.txt
python3 manage.py provider_payout