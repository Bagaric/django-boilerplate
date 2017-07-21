#!/usr/bin/env python
import sys
import os
from subprocess import call
from getpass import getpass
from time import sleep

import boto3
from github import Github
from github.GithubException import BadCredentialsException
from paramiko.client import SSHClient
from paramiko.ssh_exception import NoValidConnectionsError
import paramiko

"""
List of files that contains project variables.
"""
FILE_LIST = [
    './docker-compose.yml',
    './Makefile',
    './README.md',
    'config/nginx/nginx.conf',
    'config/postgres/init.sql',
    'config/scripts/build.sh',
    'config/scripts/deploy.sh',
    'src/env-staging',
]


def main():

    app_name = input("What is the name of your app? (snake_case): ")
    staging_host = input("Staging host or IP: ") if query_yes_no(
        "Does your app already have a staging host?", default="no") else None
    prod_host = input("Prod hostname or IP: ") if query_yes_no(
        "Does your app already have a prod host?", default="no") else None
    use_git = query_yes_no("Do you want to initialize a GitHub repo?")

    set_variables(app_name, staging_host, prod_host)

    if use_git:
        git_repo_url = init_git_repo(app_name)
        init_ec2_instance(app_name, git_repo_url)

    print("Finished.")


def init_git_repo(app_name):
    """
    Initializes the GitHub repo for the app.
    """
    print("Creating the GitHub repo...")

    while True:
        try:
            github_username = input("GitHub username: ")
            github_password = getpass(prompt="GitHub password: ")

            github = Github(github_username, github_password)
            user = github.get_user()
            repo = user.create_repo(to_camel_case(app_name))
        except BadCredentialsException:
            print("Wrong username/password. Try again.")
        else:
            break

    commands = """mkdir ../{0}
rsync -av --exclude='venv' --exclude='requirements.txt' --exclude='setup.py' * ../{0}
git init
git add -A
git commit -m 'Initial commit'
git remote add origin {1}
git push -u origin master""".format(app_name, repo.ssh_url)

    for command in commands.split('\n'):
        if command == "git init":
            os.chdir(os.path.dirname(os.getcwd()) + "/" + app_name)
        call(command, shell=True)

    return repo.ssh_url


def init_ec2_instance(app_name, git_repo_url):
    """
    Creates and runs an EC2 instance.
    """
    print("Creating an EC2 instance...")

    ec2 = boto3.resource('ec2')
    ec2.create_instances(
        ImageId='ami-835b4efa',
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        KeyName='keypair1',
        SecurityGroupIds=[
            'sg-8c5df1f6',
        ],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': app_name
                    },
                ]
            },
        ]
    )

    instances = ec2.instances.all()
    for i in instances:
        if i.tags:
            if i.tags[0]['Value'] == app_name:
                instance = i
                break

    print("Waiting for the EC2 instance to start... (This may take a few minutes)")
    instance.wait_until_running()

    print("SSHing into the instance...")
    ssh = SSHClient()
    keypair = paramiko.RSAKey.from_private_key_file(
        "/Users/bagaricj/keypair1.pem")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connected = False
    while not connected:
        try:
            ssh.connect(hostname=instance.public_ip_address,
                        pkey=keypair, username="ubuntu")
        except NoValidConnectionsError:
            continue
        connected = True

    print("Copying necessary files to the instance...")
    sftp = ssh.open_sftp()
    sftp.put("/Users/bagaricj/.ssh/id_rsa", "/home/ubuntu/.ssh/id_rsa")
    sftp.put("/Users/bagaricj/.ssh/id_rsa.pub", "/home/ubuntu/.ssh/id_rsa.pub")
    ssh.exec_command("chmod 0400 ~/.ssh/id_rsa*")
    ssh.exec_command("echo -e 'Host github.com\n    StrictHostKeyChecking no\n' >> ~/.ssh/config")

    print("Cloning the repo on the instance...")
    ssh.exec_command("git clone " + git_repo_url)

    ssh.close()


def set_variables(app_name, staging_host, prod_host):
    """
    Sets all variables in the project.
    """
    print("Replacing placeholder variables in files...")

    find_replace("app_name", app_name if app_name else "app_name")
    find_replace("staging_host", staging_host if staging_host else "")
    find_replace("prod_host", prod_host if prod_host else "")


def find_replace(keyword, value, files=FILE_LIST):

    find = "{$" + keyword + "}"

    for filename in files:
        with open(filename, "r") as f:
            file_content = f.read()

        file_content = file_content.replace(find, value)
        with open(filename, "w") as f:
            f.write(file_content)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def to_camel_case(snake_str):
    components = snake_str.split('_')
    return "".join(x.title() for x in components)

if __name__ == "__main__":
    main()
