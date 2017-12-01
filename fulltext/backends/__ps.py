# To create a postscript file for test:
# enscript -B --word-wrap -ptest.ps test.txt

from __future__ import absolute_import

import logging

from fulltext.util import run, which, warn


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


if which('pstotext') is None:
    warn('CLI tool "pstotext" is required for .ps backend.')


def _get_file(f, **kwargs):
    out = run('pstotext', '-', stdin=f)
    return out.decode(kwargs['encoding'], kwargs['encoding_errors'])


def _get_path(path, **kwargs):
    out = run('pstotext', path)
    return out.decode(kwargs['encoding'], kwargs['encoding_errors'])
