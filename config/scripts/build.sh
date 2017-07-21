#!/bin/sh
cd ~/{$app_name_camelcase}
. venv/bin/activate
git pull origin master
pip install -r config/requirements.txt
pip uninstall -y docker docker-py docker-compose
pip install docker-compose
cd src
./manage.py collectstatic --noinput
cd ~/{$app_name_camelcase}
make rebuild-local