#!/usr/bin/env python3
import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import glob
import os
import shlex
import shutil
import subprocess
import sys
import time

from svcutils.service import Config, ConfigNotFound

ZERO_FILENAME = '.purgevm.zero'
SHUTDOWN_DELAY = 5


@dataclass
class Cleaner:
    requires: str
    cmds: list


CLEANERS = {
    'apt': Cleaner('apt', ['sudo apt -y clean', 'sudo apt -y autoclean', 'sudo apt -y autoremove']),
    'docker': Cleaner('docker', ['sudo docker system prune -a --volumes -f']),
    'journal': Cleaner('journalctl', ['sudo journalctl --vacuum-time=2d']),
    'npm': Cleaner('npm', ['npm cache clean --force']),
    'snap': Cleaner('snap', ["sudo sh -c 'rm -rf /var/lib/snapd/cache/*'"]),
}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=os.getcwd(), help='directory containing user_settings.py')
    parser.add_argument('-n', '--dry-run', action='store_true', help='print what would be done and exit')
    parser.add_argument('-s', '--shutdown', action='store_true', help='shutdown after cleaning')
    parser.add_argument('-f', '--force', action='store_true', help='run even if not on a vm')
    return parser.parse_args()


def is_vm():
    if not shutil.which('systemd-detect-virt'):
        return False
    return subprocess.run(['systemd-detect-virt', '--vm', '--quiet']).returncode == 0


def expand_path(pattern):
    pattern = os.path.expanduser(pattern)
    dirname, basename = os.path.split(pattern)
    paths = glob.glob(pattern, recursive=True)
    if basename.startswith('*'):    # glob skips hidden files
        paths += glob.glob(os.path.join(dirname, f'.{basename}'), recursive=True)
    return paths


def is_tmpfs(path):
    result = subprocess.run(['findmnt', '-n', '-o', 'FSTYPE', '--target', path], capture_output=True, text=True)
    return result.stdout.strip() == 'tmpfs'


class ProcessManager:
    def __init__(self, cmd):
        self.cmd = cmd

    def is_running(self):
        result = subprocess.run(['pgrep', '-x', self.cmd], capture_output=True)
        return result.returncode == 0

    def stop(self):
        subprocess.run(['pkill', '-SIGTERM', '-x', self.cmd], check=False)
        while self.is_running():
            print(f'waiting for {self.cmd} to stop...')
            time.sleep(1)
        print(f'{self.cmd} stopped successfully')

    def start(self):
        try:
            subprocess.Popen([self.cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            print(f'{self.cmd} started successfully')
        except Exception as e:
            print(f'Failed to start {self.cmd}: {e}')
            return False
        return True


@contextmanager
def processes_stopped(cmds):
    running = [m for m in map(ProcessManager, cmds) if m.is_running()]
    try:
        for manager in running:
            print(f'stopping {manager.cmd}...')
            manager.stop()
        yield
    finally:
        for manager in running:
            print(f'restarting {manager.cmd}...')
            manager.start()


class Purger:
    def __init__(self, config, dry_run=False):
        self.config = config
        self.dry_run = dry_run
        self.failures = []

    def _fail(self, description, error):
        print(f'Error: {error}')
        self.failures.append(description)

    def run_command(self, cmd, description, check=True):
        print('*' * 80)
        print(description)
        if self.dry_run:
            print(f'would run: {cmd}')
            return True
        try:
            subprocess.run(cmd, text=True, stdout=sys.stdout, stderr=sys.stderr, shell=True, check=check)
        except subprocess.CalledProcessError as e:
            self._fail(description, e)
            return False
        return True

    def remove_path(self, path):
        if self.dry_run:
            print(f'would remove: {path}')
            return
        try:
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except FileNotFoundError:
            pass
        except PermissionError:
            try:
                subprocess.run(['sudo', 'rm', '-rf', '--', path], check=True)
            except subprocess.CalledProcessError as e:
                self._fail(f'removing {path}', e)
        except OSError as e:
            self._fail(f'removing {path}', e)

    def purge_paths(self):
        print('*' * 80)
        print('removing paths')
        for pattern in self.config.PURGE_PATHS:
            for path in expand_path(pattern):
                self.remove_path(path)

    def run_cleaners(self):
        for name in self.config.ENABLED_CLEANERS:
            cleaner = CLEANERS[name]
            if not shutil.which(cleaner.requires):
                print(f'skipping {name}: {cleaner.requires} not found')
                continue
            for cmd in cleaner.cmds:
                self.run_command(cmd, f'cleaning {name}')

    def zero_free_space(self):
        for zero_dir in self.config.ZERO_DIRS:
            zero_dir = os.path.expanduser(zero_dir)
            if is_tmpfs(zero_dir):
                self._fail(f'zeroing {zero_dir}', f'{zero_dir} is on tmpfs, not on disk')
                continue
            zero_file = shlex.quote(os.path.join(zero_dir, ZERO_FILENAME))
            try:
                # dd fails with ENOSPC once the free space is filled
                self.run_command(f'dd if=/dev/zero of={zero_file} bs=8M', f'zeroing free space of {zero_dir}',
                                 check=False)
            finally:
                self.run_command(f'rm -f {zero_file}', f'cleaning {zero_file}')

    def get_drive_usage(self):
        self.run_command('sudo du -xah / | sort -hr | head -n 50', 'getting drive usage')

    def shutdown(self):
        print(f'shutting down in {SHUTDOWN_DELAY} seconds...')
        if not self.dry_run:
            time.sleep(SHUTDOWN_DELAY)
        self.run_command('sudo shutdown -h now', 'shutting down')

    def run(self, shutdown=False):
        self.purge_paths()
        self.run_cleaners()
        if self.dry_run:
            self.zero_free_space()
        else:
            with processes_stopped(self.config.STOP_PROCESSES):
                self.zero_free_space()
        self.get_drive_usage()
        if self.failures:
            print(f'Failed: {", ".join(self.failures)}')
        if shutdown:
            self.shutdown()
        return 1 if self.failures else 0


def main():
    if sys.platform != 'linux':
        print(f'Error: {sys.platform} is not supported')
        return 1
    args = get_args()
    if not (args.force or is_vm()):
        if not args.dry_run:
            print('Error: not on a vm, nothing was purged (use --force to override)')
            return 1
        print('Warning: not on a vm, a real run would be refused (use --force to override)')
    path = os.path.realpath(os.path.expanduser(args.path))
    try:
        config = Config(os.path.join(path, 'user_settings.py'),
                        PURGE_PATHS=[], ENABLED_CLEANERS=[], STOP_PROCESSES=[], ZERO_DIRS=[])
    except ConfigNotFound as e:
        print(f'Error: settings file {e} not found, nothing was purged')
        return 1
    unknown = set(config.ENABLED_CLEANERS) - set(CLEANERS)
    if unknown:
        print(f'Error: unknown cleaners: {", ".join(sorted(unknown))}, available: {", ".join(CLEANERS)}')
        return 1
    return Purger(config, dry_run=args.dry_run).run(shutdown=args.shutdown)


if __name__ == "__main__":
    sys.exit(main())
