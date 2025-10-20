import argparse
from collections import defaultdict
from datetime import datetime
import os
from pathlib import Path
import time

EXCLUDE_PATH_PARTS = {'__pycache__', '.cache', '.git', 'cache', 'htmlcache', 'logs', 'temp', 'D3DSCache', 'NVIDIA'}
EXCLUDE_PATH_SUBSTRINGS = {'\\Microsoft\\Edge\\', '\\Microsoft.XboxGamingOverlay', '\\MicrosoftWindows.Client.'}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-dir', '-r', type=str, default=os.path.dirname(os.path.expanduser('~')),
                        help='root directory')
    parser.add_argument('--mtime-delta', '-m', type=int, default=3600,
                        help='mtime delta in seconds')
    return parser.parse_args()


def walk_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)


def get_path_parts_pathlib(path):
    return list(Path(path).parts)


def main():
    args = parse_args()
    by_parent = defaultdict(list)
    for file in walk_files(args.root_dir):
        try:
            mtime = os.path.getmtime(file)
        except FileNotFoundError:
            continue
        if mtime < time.time() - args.mtime_delta:
            continue
        parent = os.path.dirname(file)
        parts = set(Path(file).parts)
        if any(p in EXCLUDE_PATH_PARTS for p in parts):
            continue
        if any(s in parent for s in EXCLUDE_PATH_SUBSTRINGS):
            continue
        by_parent[parent].append(mtime)
    agg = {k: max(v) for k, v in by_parent.items()}
    for parent, mtime in sorted(agg.items(), key=lambda x: x[1]):
        print(f'{datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}  {parent}')


if __name__ == '__main__':
    main()
