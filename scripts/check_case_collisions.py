"""Reject tracked paths that cannot coexist on case-insensitive filesystems."""
from collections import defaultdict
from pathlib import Path
import subprocess
import sys


def find_collisions(paths):
    groups = defaultdict(list)
    for path in paths:
        groups[path.casefold()].append(path)
    return [group for group in groups.values() if len(group) > 1]


def main():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ['git', '-c', f'safe.directory={root.as_posix()}', 'ls-files', '-z'],
        cwd=root, capture_output=True, check=True,
    )
    collisions = find_collisions(result.stdout.decode('utf-8').rstrip('\0').split('\0'))
    for group in collisions:
        print('Case collision: ' + ' / '.join(group), file=sys.stderr)
    if collisions:
        return 1
    print('No tracked filename case collisions.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
