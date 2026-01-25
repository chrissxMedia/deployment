# deployment

`deployment` uses `git` and external tools (`siwedt`, `parcel`, `webpack`,
`make`, ...) to deploy anything, but mainly web pages.

## Security Considerations

> [!CAUTION]
> Never use the current version of `deployment` to deploy untrusted code.

The `deploy` scripts allow arbitrary code execution by design. While this can be
partially mitigated with containers and VMs, and we might explore hardening
measures in future versions, ACE is also common in many modern build systems.

## Installation

> [!NOTE]
> If you followed these steps and `deployment` keeps crashing, you're on the
> right path. Move on to [the configuration step](#configuration--usage) and
> restart afterwards.

### System service (e.g. systemd)

Because of the extreme simplicity, we currently don't have packages. Just
install Python 3.9+, `git` and `rsync` and drop `deployment.py` somewhere, like
`/usr/local/bin/deployment`.

You can drop [our config](deployment.service) into
`/etc/systemd/system/deployment.service`, or write your own,
and enable it like this:

```sh
systemctl daemon-reload
systemctl enable deployment.service --now
```

### Docker

> [!WARNING]
> Since your deployments probably need external tools, there is
> no one-size-fits-all Docker image.

For chrissx Media and _befriended projects_' (i.e. projects/people we provide
hosting to) deployments we only require `npm`. Therefore, we provide
[an `ubuntu:latest`-based image containing `deployment` and Node 24](Dockerfile):

> [!WARNING]
> This image is still new and has not been tested much.
> Expect to run into issues.

```sh
docker run -d --restart=unless-stopped --pull=always --init -v$PWD/deployments.csv:/etc/deployments.csv -v$PWD/deployment-data:/var/deployment chrissx/deployment:latest
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

npm ci
npm run build
```

> [!IMPORTANT]
> Please also make sure you `chmod +x` it.

> [!WARNING]
> Many build systems will leave behind Zombie Processes, which count towards
your system's process limit (`ulimit -n`). Cleaning them up is part of `init`'s
job. Therefore, Docker containers should use
[`tini`](https://github.com/krallin/tini) (`--init`), unless you have verified
that your `deploy` scripts don't leave anything behind.

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
| `--dry-run`     | `-n`       | **False**              | Prints commands but doesn't execute them (can't predict `rsync`/`-D`)   |
