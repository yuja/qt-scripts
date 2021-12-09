#!/usr/bin/env python3

import argparse
import fnmatch
import json
import os
import re
import sys


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


def dump_json(data, f):
    json.dump(data, f, indent=4, sort_keys=True)
    f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-I", "--include", action="append")
    ap.add_argument("-o", "--output")
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()
    if args.include:
        include_pat = re.compile(
            "|".join("(?:%s)" % fnmatch.translate(p) for p in args.include)
        )
    else:
        include_pat = re.compile(r".*")
    files = sorted(map(os.path.relpath, collect_files(args.paths, include_pat)))

    data = {}
    if args.output:
        with open(args.output, "r") as f:
            data.update(json.load(f))
    data["files"] = files
    if args.output:
        with open(args.output + ".new", "w") as f:
            dump_json(data, f)
        os.rename(args.output + ".new", args.output)
    else:
        dump_json(data, sys.stdout)


if __name__ == "__main__":
    main()
