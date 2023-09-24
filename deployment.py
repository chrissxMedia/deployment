#!/usr/bin/env python3
from csv import reader
from os import chdir
from os.path import exists
from subprocess import run
from time import sleep
from traceback import print_exc
from argparse import ArgumentParser


def shell(cmd, **kwargs):
    print(cmd)
    run(cmd, shell=True, check=True, **kwargs)


parser = ArgumentParser(description='chrissx Media Deployment Manager')
parser.add_argument('--clone-only', action='store_true')
parser.add_argument('-d', '--deployments', default='/etc/deployments.csv')
args = parser.parse_args()

# TODO: consider adding the config file as an arg
deployments = []
with open(args.deployments, encoding='utf-8') as f:
    for line in reader(f):
        deployments.append(tuple(line))
        if not exists(line[0]):
            shell(f'git clone "{line[1]}" "{line[0]}"')

if args.clone_only:
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
                # TODO: redirected stdout/err
                run('./deploy')
        except Exception as e:
            print_exc()
        sleep(30)
