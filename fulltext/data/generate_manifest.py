#!/usr/bin/env python

"""
Generate MANIFEST.in file.
"""

import os
import subprocess


IGNORED_EXTS = []
IGNORED_FILES = ['.travis.yml', 'appveyor.yml']
IGNORED_PREFIXES = ["files/"]


def sh(cmd):
    return subprocess.check_output(
        cmd, shell=True, universal_newlines=True).strip()


def main():
    files = sh("git ls-files").split('\n')
    for file in files:
        if file.startswith('.ci/') or \
                os.path.splitext(file)[1].lower() in IGNORED_EXTS or \
                file in IGNORED_FILES:
            continue

        for prefix in IGNORED_PREFIXES:
            if file.startswith(prefix):
                break
        else:
            print("include " + file)


if __name__ == '__main__':
    main()
