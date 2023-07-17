# deployment

`deployment` uses `git` and external tools (`siwedt`, `parcel`, `webpack`,
`make`, ...) to deploy anything, but mainly webpages.

## Installation

Because of the extreme simplicity, we currently don't have packages. Just drop
`deployment.py` somewhere, like `/usr/local/bin/deployment`.

If you wanted to, you could just run it in your shell, but of course we don't
recommend that. If you use another init system, you'll have to figure it out
yourself, but for `systemd` just create a file at
`/etc/systemd/system/deployment.service` that can be as simple as this:

```ini
[Unit]
Description=chrissx Media deployment manager

[Service]
ExecStart=/usr/local/bin/deployment

[Install]
WantedBy=multi-user.target
```

And then enable it:

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
/var/www/site1,https://git.chrissx.de/site1.git,
/var/www/site2,https://git.chrissx.de/site2.git,
```

The comma at the end is currently an unnecessary idiom, because of the now
deprecated support for build commands specified in the deployments file itself:

```csv
/var/www/site3,https://git.chrissx.de/site3.git,npm install && npm run build
```

**Don't do that!** `deploy` scripts are the way forward and the third field in
the `deployments.csv` will probably be removed at some point. However,
specifying it won't ever break `deployment`, so you can put it in as a fallback
if you really want to.

What you really want is a file called `deploy` at the root of your Git
repository that is then automatically executed by `deployment`. It might look
something like this:

```sh
#!/bin/sh
set -uxe

npm install
npm run build
```

Please also make sure you `chmod +x` it.
