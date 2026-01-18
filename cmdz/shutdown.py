import logging
import subprocess
import sys

from vbox.virtualbox import Virtualbox

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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


def main():
    try:
        Virtualbox(headless=False).stop_all_vms(save=True)
    except FileNotFoundError as e:
        logger.debug(str(e))
    if sys.platform == 'win32':
        for proc in ['VBoxSVC.exe', 'VirtualBox.exe', 'VBoxHeadless.exe', 'VirtualBoxVM.exe']:
            taskkill(proc)
        run('shutdown /s /t 0')
    else:
        run('systemctl poweroff')


if __name__ == '__main__':
    main()
