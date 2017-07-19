#!/bin/sh
rm -rf ~/{$app_name}
git clone <github_url> ~/{$app_name}
cd ~/{$app_name}
python -m virtualenv --python=/usr/bin/python3 venv
. venv/bin/activate
pip install -r config/requirements.txt
pip uninstall -y docker docker-py docker-compose
pip install docker-compose
cd src
./manage.py collectstatic --noinput
cd ~/{$app_name}
make rebuild-local
rm -rf ~/.ssh/github_rsa*