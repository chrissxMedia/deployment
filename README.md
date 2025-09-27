# deployment

`deployment` uses `git` and external tools (`siwedt`, `parcel`, `webpack`,
`make`, ...) to deploy anything, but mainly webpages.

## Installation

Because of the extreme simplicity, we currently don't have packages. Just
install Python 3.9+ and `rsync` and drop `deployment.py` somewhere, like
`/usr/local/bin/deployment`.

If you wanted to, you could just run it in your shell, but of course we don't
recommend that. If you use another init system, you'll have to figure it out
yourself, but for `systemd` you can drop [our config](deployment.service)
into `/etc/systemd/system/deployment.service`, and enable it like this:

```sh
systemctl daemon-reload
systemctl enable deployment.service --now
```

If you now checked `systemctl status deployment.service` and found it to have
already crashed, it's probably because you haven't created the configuration
yet. That's the next step.

## Configuration & Usage

`deployment` reads a list of deployments from `/etc/deployments.csv`, which
looks like this:

```csv
/var/www/site1,https://git.chrissx.de/site1.git
/var/www/site2,https://git.chrissx.de/site2.git
```

Now create a file called `deploy` at the root of every Git repository that is
then automatically executed by `deployment`. It might look something like this:

```sh
#!/bin/sh
set -uxe

npm install
npm run build
```

Please also make sure you `chmod +x` it.
