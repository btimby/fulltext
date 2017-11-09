"""
Fulltext CLI interface.
"""

from __future__ import absolute_import

import sys
import logging

from docopt import docopt

import fulltext


def _handle_open(path):
    with open(path, 'rb') as f:
        return fulltext.get(f)


def main(args=sys.argv[1:]):
    """
    Extract text from a file.

    Usage:
        fulltext [-f] <path>...

    Options:
        -f      Open file first.
    """
    opt = docopt(main.__doc__.strip(), args, options_first=True)

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())

    handler = fulltext.get

    if opt['-f']:
        handler = _handle_open

    for path in opt['<path>']:
        print(handler(path))


if __name__ == '__main__':
    main()
