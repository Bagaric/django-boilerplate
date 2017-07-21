#!/usr/bin/env python
import os
import sys
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

    if 'test' in sys.argv:
        env_file = "env-test"
    else:
        if os.environ.get("ENV") == "prod":
            env_file = "env-prod"
        elif os.environ.get("ENV") == "staging":
            env_file = "env-staging"
        else:
            env_file = "env-dev"
    if not os.path.isfile(env_file):
        print("environment variable file {} does not exist; please create it to enter your DB config and other environment-specific configurations".format(env_file))
        sys.exit(1)

    line_num = 1
    with open(env_file, 'r') as f:
        for line in f:
            line_parts = line.split("=")
            if len(line_parts) != 2:
                print("error in environment variable file {} on line {}: {}: cannot continue".format(env_file, line_num, line))
                sys.exit(1)
            os.environ.setdefault(line_parts[0], line_parts[1].strip())
            line_num += 1

    execute_from_command_line(sys.argv)