#!/bin/sh
rm -rf ~/testapp
git clone <github_url> ~/testapp
cd ~/testapp
python -m virtualenv --python=/usr/bin/python3 venv
. venv/bin/activate
pip install -r config/requirements.txt
pip uninstall -y docker docker-py docker-compose
pip install docker-compose
cd src
./manage.py collectstatic --noinput
cd ~/testapp
make rebuild-local
rm -rf ~/.ssh/github_rsa*