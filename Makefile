help:
	@echo "--local--"
	@echo "build-local - Build container locally"
	@echo "rebuild-local - Rebuild local containers"
	@echo "delete-local - Delete local containers"
	@echo "rebuild-web - Rebuilds just the web container (Django app)"
	@echo "--staging--"
	@echo "backup-db-staging - backs up the staging database into a folder ~/backup on the server"
	@echo "deploy-staging - sync local code to staging server, rebuild Docker image and reload on staging server"
	@echo "--production--"
	@echo "backup-db-production - backs up the production database into a folder ~/backup on the server"
	@echo "deploy-production - sync local code to production server, rebuild Docker image and reload on production server"

STAGING_HOST=examplestaging.com
PRODUCTION_HOST=exampleprod.com
SSH_KEY=~/keypair1.pem

build-local:
	docker-compose build
	docker-compose up -d
	docker ps -a

delete-local:
	docker-compose stop
	docker-compose rm -f

rebuild-local: delete-local build-local

rebuild-web:
	docker-compose stop web
	docker-compose rm -f web
	docker-compose build web
	docker-compose up web

backup-db-staging:
	ssh -i $(SSH_KEY) ubuntu@$(STAGING_HOST) 'bash -s' < config/scripts/backup-db.sh

deploy-staging: backup-db-staging
	ssh -i $(SSH_KEY) ubuntu@$(STAGING_HOST) 'bash -s' < config/scripts/build.sh


backup-db-production: copy-ssh-keys
	ssh -i $(SSH_KEY) ubuntu@$(PRODUCTION_HOST) 'bash -s' < config/scripts/backup-db.sh

deploy-production:: copy-ssh-keys backup-db-production
	ssh -i $(SSH_KEY) ubuntu@$(PRODUCTION_HOST) 'bash -s' < config/scripts/build.sh
	


