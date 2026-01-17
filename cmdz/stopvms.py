import argparse
import logging

from vbox.virtualbox import Virtualbox

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save', action='store_true')
    parser.add_argument('--headless', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    # Virtualbox(headless=args.headless).stop_all_vms(save=args.save)
    Virtualbox(headless=False).stop_all_vms(save=True)


if __name__ == '__main__':
    main()
