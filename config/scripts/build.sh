#!/bin/sh
cd ~/TestApp
. venv/bin/activate
git pull origin master
pip install -r config/requirements.txt
pip uninstall -y docker docker-py docker-compose
pip install docker-compose
cd src
./manage.py collectstatic --noinput
cd ~/TestApp
make rebuild-local