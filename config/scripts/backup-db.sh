#!/bin/sh
cd ~/testapp
. venv/bin/activate
docker-compose exec -T db pg_dumpall -c -U postgres > ~/backup/db/dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
docker-compose exec -T web python manage.py dumpdata > ~/backup/db/dump_`date +%d-%m-%Y"_"%H_%M_%S`.json