#!/usr/bin/env python3
from csv import reader
from os import chdir
from os.path import exists
from subprocess import run
from sys import argv
from time import sleep
from traceback import print_exc


def shell(cmd, **kwargs):
    print(cmd)
    run(cmd, shell=True, check=True, **kwargs)

# TODO: consider adding the config file as an arg
deployments = []
with open('/etc/deployments.csv', encoding='utf-8') as f:
    for line in reader(f):
        deployments.append(tuple(line))
        if not exists(line[0]):
            shell(f'git clone "{line[1]}" "{line[0]}"')

if len(argv) >= 2 and argv[1] == "--clone-only":
    exit(0)

while True:
    for deployment in deployments:
        try:
            # TODO: should deploy still run if we cant pull?
            print('cd ' + deployment[0])
            chdir(deployment[0])
            shell('git pull')
            if not exists('deploy'):
                shell(deployment[2])
            else:
                # TODO: redirected stdout/err and check=False
                run('./deploy')
        except Exception as e:
            print_exc()
        sleep(30)
