"""
Fulltext CLI interface.
"""

from __future__ import absolute_import, print_function

import os
import sys
import logging

from docopt import docopt

import fulltext
from fulltext.util import hilite


HERE = os.path.abspath(os.path.dirname(__file__))


def _handle_open(path):
    with open(path, 'rb') as f:
        return fulltext.get(f)


def check_backends():
    """Invoke test() for all backends and fail (raise) if some dep
    is missing.
    """
    path = os.path.join(HERE, "backends")
    errs = []
    for name in os.listdir(path):
        if not name.endswith('.py'):
            continue
        mod_name = "fulltext.backends.%s" % (
            os.path.splitext(os.path.basename(name))[0])
        mod = __import__(mod_name, fromlist=[' '])
        if hasattr(mod, "check"):
            try:
                mod.check()
            except Exception as err:
                errs.append((mod, str(err)))
    if errs:
        for mod, err in errs:
            msg = hilite("%s: %s" % (mod.__name__, err), ok=False)
            print(msg, file=sys.stderr)
        sys.exit(1)


def main(args=sys.argv[1:]):
    """Extract text from a file.

    Commands:
        extract - extract text from path
        test    - make sure all deps are installed

    Usage:
        fulltext extract [-f] [-t] <path>...
        fulltext test

    Options:
        -f      Open file first.
    """
    opt = docopt(main.__doc__.strip(), args, options_first=True)

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())

    if opt['test']:
        check_backends()
    else:
        handler = fulltext.get

        if opt['-f']:
            handler = _handle_open

        for path in opt['<path>']:
            print(handler(path))


if __name__ == '__main__':
    main()
