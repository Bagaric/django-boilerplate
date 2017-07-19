# {?app_name}

Deployment instructions and notes

## Running a local build

In the project root directory, create a virtual environment and download required python modules:

`virtualenv --python=/usr/bin/python3.5 venv`

`source venv/bin/activate`

`pip install -r config/requirements.txt`

Open a new terminal window - don't forget to source your virtual env again:

`cd src/`

`python manage.py migrate`

You can now use these credentials to log in as an admin:
Username: `admin`
Password: `login123`

`python manage.py runserver`

## Staging on an AWS EC2 instance

### Nuts and bolts

Create an EC2 instance using the Ubuntu 16.04 AMI that

* has a public IP address
* is in a security group which allows all inbound traffic on
    * SSH 22
    * HTTP 80
    * HTTPS 443
* allows all outbound traffic
* has a key pair associated with it
	* hint: set up ~/.ssh/config for an easier life

### DNS settings

* In the AWS console, create a Hosted Zone for your domain.
* On the registrar's website, update your DNS records to contain only the 4 NS NameServer records in your hosted zone.
* In the AWS Hosted Zone, create 2 A records using the instance IP address
	* one pointing to the naked domain
	* one pointing to www.*
* In a production setting, an elastic IP should be used so that a recreated instance will have the same IP (and thus avoid DNS misconfiguration in the event of downage)

### Server setup

The plain Ubuntu 16.04 AMI doesn't come with all batteries included. SSH to your instance and

* `sudo apt-get update`
* `sudo install make`
* `sudo install docker.io`
* `sudo usermod -A -G docker ubuntu` (to allow nonroot docker access. Also requires you to log out and back in)

The final command may need adjusting if the nginx settings happen to use a slightly different directory

### Makefile

The build and deployment process is controlled using the ``make`` tool. 
You can control the build process entirely from your local workstation using the ``make`` tool (no need to be logged into the server). The make tool will sync the local code to the server and restart the web app.
To see a list of available commands, switch to the project root directory and type:

```
make
```

You can run the commands under the "staging" sections on your local development workstation.
You can are able to to control evertyhing you need for typical operation from your local workstation.

Before running any commands, make sure to change the Makefile entry "SSH_KEY" to match the path to your AWS SSH key.


### Staging Deployment


#### Initial build

We are now ready to build the Docker image for the first time. Log out of the server and switch to the project directory on your local workstation.
Please note that for operation from your local workstation, you must be able to access the staging server via SSH.

You only have to build the Docker image each time there is a change to system config or Python dependencies (but at least once).
Switch to the top-level repository directory and (re)build the Django Docker image:

`make build-staging`

On your local workstation, run the following command to start the new Docker image on the staging server:

`make run-staging` or `make restart-staging` if it already exists

If you would like to sync your changes without restarting your server, use the following command:

`make deploy-staging`

If you made system configuration changes or changes to the requirements.txt file, use the following command to completely 
rebuild the Docker image (this is rarely necessary):
  
`make build-staging`


### Production Deployment

Nearly identical to the staging deployment process. Check the `env-*` files and the relevant `make` commands

### Debugging hints

Having basic knowledge of Docker and Docker-compose really helps in this part.

The server should contain 3 docker images, and all of them should be up and running:
* nginx - Web server docker instance
* web - Django application itself
* db - PostgreSQL database

They are logically separated and connect to each other. All the data from the server is stored in the PostgreSQL database container.
Be sure to regularly backup the database container in order to avoid losing data.

* `docker ps -a` - To check which docker containers are up and which are down
* `docker-compose logs web` to check for any errors of the webserver
    * `service nginx status`
    * `cat /var/log/nginx/error.log`
* `docker info`
* `nc -v <HOSTNAME> <PORT>`

### Possible improvements and other notes

* better automation
* Adding SSL to the staging server
* convert `env-*` files to actual Python modules instead of parsing manually
* de-duplicate tangled `static` and `staticfiles` directory situation