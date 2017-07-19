#!/bin/sh
cd ~/{$app_name}
. venv/bin/activate
git reset --hard HEAD
git pull origin master
make rebuild-web
rm -rf ~/.ssh/github_rsa*