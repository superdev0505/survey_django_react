#!/usr/bin/env bash

export APP_DEBUG=True

while getopts ":p:u:b:ip:" opt; do
  case $opt in
    p) provider="$OPTARG"
    ;;
    u) user="$OPTARG"
    ;;
    b) btc="$OPTARG"
    ;;
    ip) ip="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done


python3 manage.py integration_test_survey -p "$provider" -u "$user" -b "$btc" -ip "$ip"