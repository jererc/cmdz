import argparse
import os
from pathlib import PurePosixPath, Path
import re
import unicodedata

RE_REMOVE = re.compile(r'[\n\r]+')
RE_SPECIAL = re.compile(r'[\t\*\:\;\?\|\"\'\<\>]+')
RE_SPACE = re.compile(r'[\s_]+')


def walk_path(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for item in sorted(files + dirs):
            yield str(Path(PurePosixPath(os.path.join(root, item))))


def iterate_paths(paths):
    for path in paths:
        yield from walk_path(path)


def remove_accents(text):
    # Normalize the text to "NFD" form (decomposed)
    normalized = unicodedata.normalize('NFD', text)
    # Filter out all combining characters (accents, etc.)
    return ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')


def clean_name(name):
    name = RE_REMOVE.sub('', name)
    name = RE_SPECIAL.sub('_', name)
    name = remove_accents(name)
    return RE_SPACE.sub('_', name).strip('_')


def get_new_path(path, dirname_callable=None, filename_callable=None):
    def clean(name, is_dir=False):
        res = clean_name(name)
        if is_dir and dirname_callable:
            res = dirname_callable(res)
        elif not is_dir and filename_callable:
            res = filename_callable(res)
        return res

    head, tail = os.path.split(path)
    if os.path.isdir(path):
        return os.path.join(head, clean(tail, is_dir=True))
    else:
        root, ext = os.path.splitext(tail)
        return os.path.join(head, f'{clean(root, is_dir=False)}{ext.lower()}')


def clean_paths(paths, dirname_callable=None, filename_callable=None):
    to_rename = []
    for path in iterate_paths(paths):
        new_path = get_new_path(path, dirname_callable=dirname_callable, filename_callable=filename_callable)
        if new_path and new_path != path:
            to_rename.append((path, new_path))
    if not to_rename:
        return
    for old_path, new_path in to_rename:
        print(f'{old_path=}\n{new_path=}')
    input('continue?')
    for old_path, new_path in to_rename:
        os.rename(old_path.encode('utf-8'), new_path)
        print(f'renamed {old_path=} to {new_path=}')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--lower', action='store_true')
    parser.add_argument('--lower-dir', action='store_true')
    parser.add_argument('--capitalize', action='store_true')
    parser.add_argument('--capitalize-dir', action='store_true')
    return parser.parse_args()


def _lower(x):
    return x.lower()


def _capitalize(x):
    return x.title()


def main():
    args = parse_args()
    if args.lower:
        filename_callable = _lower
    elif args.capitalize:
        filename_callable = _capitalize
    else:
        filename_callable = None
    if args.lower_dir:
        dirname_callable = _lower
    elif args.capitalize_dir:
        dirname_callable = _capitalize
    else:
        dirname_callable = None
    clean_paths(paths=args.paths, dirname_callable=dirname_callable, filename_callable=filename_callable)


if __name__ == '__main__':
    main()
