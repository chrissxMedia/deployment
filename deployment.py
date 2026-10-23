#!/usr/bin/env python3
from csv import reader
from os import chdir
from os.path import exists, join
from subprocess import run
from time import sleep, time
from traceback import print_exc
from argparse import ArgumentParser
from pathlib import Path


parser = ArgumentParser(description='chrissx Media Deployment Manager')
parser.add_argument('-v', '--version', action='version', version='deployment 0.11',
                    help='show the version and exit')
parser.add_argument('-c', '--clone-only', action='store_true',
                    help='clone missing repositories and exit without pulling or building')
parser.add_argument('-d', '--deployments', default='/etc/deployments.csv',
                    help='path to the deployment CSV file (default: %(default)s)')
parser.add_argument('-H', '--home', default='/var/deployment',
                    help='base directory for relative deployment paths (default: %(default)s)')
parser.add_argument('-D', '--global-dist', action='store_true',
                    help='collect build output under HOME/dist')
parser.add_argument('-n', '--dry-run', action='store_true',
                    help='print commands without executing them or creating directories, then exit')
parser.add_argument('--delay', type=int, default=30,
                    help='seconds to wait after each deployment (default: %(default)s)')
parser.add_argument('--health-file',
                    help='write a health expiry timestamp to this file')
args = parser.parse_args()

health_file = None
if args.health_file and not args.dry_run and not args.clone_only:
    health_file = Path(args.health_file).absolute()
    health_file.unlink(missing_ok=True)


def cmd(cmd: list[str], **kwargs):
    print(cmd, flush=True)
    if not args.dry_run:
        run(cmd, shell=False, check=True, **kwargs)


deployments = []
with open(args.deployments, encoding='utf-8') as f:
    for line in reader(f):
        deployments.append(tuple(line))
        path = join(args.home, line[0])
        if not exists(path):
            cmd(['git', 'clone', line[1], path])

if args.clone_only:
    exit(0)

first_pass = True
while True:
    healthy = True
    for deployment in deployments:
        try:
            # TODO: should deploy still run if we cant pull?
            path = join(args.home, deployment[0])
            if args.dry_run and not exists(path):
                continue
            print('cd ' + path, flush=True)
            chdir(path)
            cmd(['git', 'pull'])
            if exists('deploy'):
                cmd(['./deploy'])
            if args.global_dist and exists('dist'):
                dest = args.home + '/dist/' + deployment[0].lstrip('/')
                if not args.dry_run:
                    Path(dest).mkdir(parents=True, exist_ok=True)
                cmd(['rsync', '-aHhE', '--remove-source-files',
                    '--delete-after', '--delay-updates', 'dist', dest])
        except Exception as e:
            print_exc()
            healthy = False
            if health_file:
                health_file.unlink(missing_ok=True)
        if not args.dry_run and not first_pass:
            sleep(args.delay)
    if args.dry_run:
        exit(0)
    if health_file and healthy and deployments:
        health_file.write_text(str(time() + len(deployments) * args.delay * 2))
    first_pass = False
