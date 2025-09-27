# deployment

`deployment` uses `git` and external tools (`siwedt`, `parcel`, `webpack`,
`make`, ...) to deploy anything, but mainly webpages.

## Installation

> [!NOTE]
> If you followed these steps and `deployment` keeps crashing, you're on the
> right path. Just move on to the configuration step and restart afterwards.

## Docker

> [!WARNING]
> The Docker image is still new and has not been tested much.
> Expect to run into issues.

```sh
docker run -d --restart=unless-stopped --pull=always -v$PWD/deployments.csv:/etc/deployments.csv -v$PWD/deployment-data:/var/deployment chrissx/deployment:latest
```

## systemd

Because of the extreme simplicity, we currently don't have packages. Just
install Python 3.9+ and `rsync` and drop `deployment.py` somewhere, like
`/usr/local/bin/deployment`.

You can drop [our config](deployment.service) into
`/etc/systemd/system/deployment.service`, or write your own,
and enable it like this:

```sh
systemctl daemon-reload
systemctl enable deployment.service --now
```

## Configuration & Usage

`deployment` reads a list of deployments from `/etc/deployments.csv`
([configurable](#options)), which looks like this:

```csv
/var/www/site1,https://git.chrissx.de/site1.git
site2,https://git.chrissx.de/site2.git
```

Deployments starting with a forward slash (`/`) are interpreted as absolute
paths, deployments without a leading slash live in the `deployment` _Home_.
In this example, `site1` lives at `/var/www/site1` and `site2` lives at
`/var/deployment/site2` ([configurable](#options)).

Now create a file called `deploy` at the root of every Git repository that is
then automatically executed by `deployment`. It might look something like this:

```sh
#!/bin/sh
set -uxe

npm install
npm run build
```

Please also make sure you `chmod +x` it.

If a repository does not have a `deploy` script, `deployment` will just keep it
up to date (`git pull`).

### Options

| Long flag       | Short flag | Default                | Purpose / Note                                                          |
|-----------------|------------|------------------------|-------------------------------------------------------------------------|
| `--clone-only`  | `-c`       | **False**              | Only clone the `git` repositories and exit, don't pull or build         |
| `--deployments` | `-d`       | `/etc/deployments.csv` | Path to the deployment list                                             |
| `--home`        | `-H`       | `/var/deployment`      | `deployment` _Home_ (explained above)                                   |
| `--global-dist` | `-D`       | **False**              | Copy all `dist` directories to the _Home_ (e.g. `/var/deployment/dist`) |
| `--delay`       | (none)     | `30` (seconds)         | Time to wait after pulling and building each deployment                 |
