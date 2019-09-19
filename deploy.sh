#!/usr/bin/env bash

if [ -z $1 ]; then
    BRANCH=master
else
    BRANCH=$1
fi;

git fetch
git reset --hard origin/$BRANCH
python3 manage.py collectstatic --noinput
cp -rn static/survey/app/build/static/ .
cp static/survey/app/build/manifest.json static/.
cp static/survey/app/build/favicon.ico static/.
service supervisor restart survey