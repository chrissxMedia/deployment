#!/usr/bin/env python3
from csv import reader
from os import chdir
from os.path import exists
from subprocess import run
from time import sleep
from traceback import print_exc
from argparse import ArgumentParser
from pathlib import Path


def shell(cmd, **kwargs):
    print(cmd)
    run(cmd, shell=True, check=True, **kwargs)


parser = ArgumentParser(description='chrissx Media Deployment Manager')
parser.add_argument('-c', '--clone-only', action='store_true')
parser.add_argument('-d', '--deployments', default='/etc/deployments.csv')
parser.add_argument('-H', '--home', default='/var/deployment')
parser.add_argument('-D', '--global-dist', action='store_true')
# TODO: configurable delay
args = parser.parse_args()


def path(d):
    return d[0] if d[0].startswith('/') else args.home + '/' + d[0]


# TODO: consider adding the config file as an arg
deployments = []
with open(args.deployments, encoding='utf-8') as f:
    for line in reader(f):
        deployments.append(tuple(line))
        if not exists(path(line)):
            shell(f'git clone "{line[1]}" "{path(line)}"')

if args.clone_only:
    exit(0)

while True:
    for deployment in deployments:
        try:
            # TODO: should deploy still run if we cant pull?
            print('cd ' + path(deployment))
            chdir(path(deployment))
            shell('git pull')
            if not exists('deploy'):
                shell(deployment[2])
            else:
                # TODO: redirected stdout/err
                run('./deploy')
            if args.global_dist and exists('dist'):
                dest = args.home + "/dist" + ('' if deployment[0].startswith('/')
                                              else '/') + deployment[0]
                Path(dest).mkdir(parents=True, exist_ok=True)
                shell(
                    'rsync -aHhE --remove-source-files --delete-after --delay-updates dist "'
                    + dest + '"')
        except Exception as e:
            print_exc()
        sleep(30)
