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


def main():
    try:
        Virtualbox(headless=False).stop_all_vms(save=True)
    except FileNotFoundError as e:
        logger.debug(str(e))
    if sys.platform == 'win32':
        run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    else:
        run('systemctl suspend')


if __name__ == '__main__':
    main()
