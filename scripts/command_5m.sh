#!/usr/bin/env bash

cd /var/www/survey
date > /var/www/monitoring.txt
python3 manage.py monitoring