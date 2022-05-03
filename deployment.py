#!/usr/bin/env python3
from csv import reader
from os import chdir
from os.path import exists
from subprocess import run
from time import sleep

def shell(cmd, **kwargs):
    run(cmd, shell=True, check=True, **kwargs)

shell('npm install -g siwedt')

deployments = []
with open('/etc/deployments.csv') as f:
    for line in reader(f):
        deployments.append(tuple(line))
        if not exists(line[0]):
            shell(f'git clone "{line[1]}" "{line[0]}"')

while True:
    for deployment in deployments:
        try:
            chdir(deployment[0])
            shell('git pull')
            if not exists('deploy'):
                shell(deployment[2])
            else:
                run('deploy')
        except:
            pass
        sleep(30)
