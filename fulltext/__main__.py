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


def check_backends(title):
    """Invoke test() for all backends and fail (raise) if some dep
    is missing.
    """
    path = os.path.join(HERE, "backends")
    errs = []
    for name in os.listdir(path):
        if not name.endswith('.py'):
            continue
        if name == '__init__.py':
            continue

        mod_name = "fulltext.backends.%s" % (
            os.path.splitext(os.path.basename(name))[0])

        try:
            mod = __import__(mod_name, fromlist=[' '])
        except ImportError as err:
            errs.append((mod_name, str(err)))
            continue

        kw = dict(encoding='utf8', encoding_errors='strict',
                  kwargs={})
        try:
            inst = getattr(mod, "Backend")(**kw)
            if hasattr(inst, "check"):
                inst.check(title=title)
        except Exception as err:
            errs.append((mod.__name__, str(err)))
    if errs:
        for mod, err in errs:
            msg = hilite("%s: %s" % (mod, err), ok=False)
            print(msg, file=sys.stderr)
        sys.exit(1)


def config_logging(verbose):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '[%(levelname)1.1s %(name)s] %(message)s'))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)


def main(args=sys.argv[1:]):
    """Extract text from a file.

    Commands:
        extract - extract text from path
        check   - make sure all deps are installed

    Usage:
        fulltext extract [-v] [-f] <path>...
        fulltext check [-t]

    Options:
        -f, --file           Open file first.
        -t, --title          Check deps for title.
        -v, --verbose        More verbose output.
    """
    opt = docopt(main.__doc__.strip(), args, options_first=True)

    config_logging(opt['--verbose'])

    if opt['check']:
        check_backends(opt['--title'])
    elif opt['extract']:
        handler = fulltext.get

        if opt['--file']:
            handler = _handle_open

        for path in opt['<path>']:
            print(handler(path))
    else:
        # we should never get here
        raise ValueError("don't know how to handle cmd")


if __name__ == '__main__':
    main()
