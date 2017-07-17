#!/usr/bin/env python
import sys
import os
import fnmatch
from getpass import getpass
import subprocess

from github import Github


def main():

    # User prompts
    app_name = input("What is the name of your app? (snake_case): ")
    staging_host = input("Staging host or IP: ") if query_yes_no(
        "Does your app already have a staging host?") else None
    prod_host = input("Prod hostname or IP: ") if query_yes_no(
        "Does your app already have a prod host?") else None
    use_git = query_yes_no("Do you want to initialize a GitHub repo?")

    set_variables(app_name, staging_host, prod_host)

    if use_git:
        init_github(app_name)

    cleanup()


def init_github(app_name):
    """
    Initializes the GitHub repo for the app.
    """

    github_username = input("GitHub username: ")
    github_password = getpass(prompt="GitHub password: ")

    g = Github(github_username, github_password)
    user = g.get_user()
    repo = user.create_repo(to_camel_case(app_name))

    return repo.ssh_url()


def set_variables(app_name, staging_host, prod_host):
    """
    Sets all variables in the project.
    """

    find_replace("app_name", app_name)

    if staging_host:
        find_replace("staging_host", staging_host)
    if prod_host:
        find_replace("prod_host", prod_host)


def cleanup():
    """
    Cleans up the directory of the setup files.
    """
    os.remove("requirements.txt")
    os.remove("setup.py")


def run_command(bash_cmd):
    process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return error


def find_replace(keyword, value):

    find = "{$" + keyword + "}"

    for path, dirs, files in os.walk(os.path.abspath(".")):
        for filename in fnmatch.filter(files, "*.*"):
            filepath = os.path.join(path, filename)
            with open(filepath) as f:
                s = f.read()
            s = s.replace(find, value)
            with open(filepath, "w") as f:
                f.write(s)


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
