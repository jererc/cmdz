import argparse
import logging
import subprocess
import sys

from vbox.virtualbox import Virtualbox

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--poweroff', action='store_true')
    return parser.parse_args()


def run(cmd):
    try:
        subprocess.run(cmd, check=True, stdout=sys.stdout, shell=True)
    except subprocess.CalledProcessError:
        logger.exception(f'failed to run {cmd=}')


def taskkill(proc):
    cmd = f'taskkill /IM {proc} /F >nul 2>nul'
    result = subprocess.run(cmd, check=False, stdout=sys.stdout, shell=True)
    if result.returncode not in [0, 128]:
        logger.error(f'failed to run {cmd=}: {result.returncode}')


def sleep():
    if sys.platform == 'win32':
        run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    else:
        run('systemctl suspend')


def poweroff():
    if sys.platform == 'win32':
        for proc in ['VBoxSVC.exe', 'VirtualBox.exe', 'VBoxHeadless.exe', 'VirtualBoxVM.exe']:
            taskkill(proc)
        run('shutdown /s /t 0')
    else:
        run('systemctl poweroff')


def main():
    try:
        Virtualbox(headless=False).stop_all_vms(save=True)
    except FileNotFoundError as e:
        logger.debug(str(e))
    poweroff() if parse_args().poweroff else sleep()


if __name__ == '__main__':
    main()
