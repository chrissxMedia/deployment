from os import environ
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory


script = Path(__file__).with_name('deployment.py').resolve()
with TemporaryDirectory() as directory:
    root = Path(directory)
    home = root / 'home'
    repo = home / 'existing'
    (repo / 'dist').mkdir(parents=True)
    (repo / 'dist' / 'index.html').write_text('build output')
    marker = root / 'executed'
    commands = root / 'bin'
    commands.mkdir()
    for command in (commands / 'git', commands / 'rsync', repo / 'deploy'):
        command.write_text(f'#!/bin/sh\ntouch "{marker}"\nexit 1\n')
        command.chmod(0o755)
    deployments = root / 'deployments.csv'
    deployments.write_text('missing,https://example.invalid/missing.git\n'
                           'existing,https://example.invalid/existing.git\n')
    for extra_args in ([], ['--clone-only']):
        result = run(['python3', str(script), '--dry-run', '--global-dist',
                      '--home', str(home), '--deployments', str(deployments),
                      *extra_args], capture_output=True, text=True, timeout=5,
                     env={**environ, 'PATH': str(commands) + ':' + environ['PATH']})
        assert result.returncode == 0, result.stderr
        assert not result.stderr, result.stderr
        assert "'git', 'clone'" in result.stdout, result.stdout
        for command in ("'git', 'pull'", "'./deploy'", "'rsync'"):
            assert (command in result.stdout) == (not extra_args), result.stdout
        assert not marker.exists()
        assert not (home / 'missing').exists()
        assert not (home / 'dist').exists()
        assert (repo / 'dist' / 'index.html').read_text() == 'build output'
print('Dry-run checks passed')
