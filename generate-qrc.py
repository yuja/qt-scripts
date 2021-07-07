#!/usr/bin/env python3

import argparse
import fnmatch
import os
import re
import sys

PROLOGUE = '''
<RCC>
    <qresource prefix="/">
'''.lstrip('\n')

EPILOGUE = '''
    </qresource>
</RCC>
'''.lstrip('\n')

ITEM = '''
        <file>{name}</file>
'''.lstrip('\n')


def collect_files(paths, include_pat):
    for top in paths:
        if not os.path.isdir(top):
            if not include_pat.match(top):
                continue
            yield top
            continue

        for root, _dirs, files in os.walk(top):
            for f in files:
                if not include_pat.match(f):
                    continue
                yield os.path.join(root, f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-I', '--include', action='append')
    ap.add_argument('paths', nargs='+')
    args = ap.parse_args()
    if args.include:
        include_pat = re.compile('|'.join('(?:%s)' % fnmatch.translate(p)
                                          for p in args.include))
    else:
        include_pat = re.compile(r'.*')
    files = sorted(map(os.path.relpath, collect_files(args.paths, include_pat)))

    sys.stdout.write(PROLOGUE)
    for name in files:
        sys.stdout.write(ITEM.format(name=name))
    sys.stdout.write(EPILOGUE)


if __name__ == '__main__':
    main()
