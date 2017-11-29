# To create a postscript file for test:
# enscript -B --word-wrap -ptest.ps test.txt

from __future__ import absolute_import

import logging

from fulltext.util import run, which, ShellError, MissingCommandException, warn


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


if which('pstotext') is None:
    warn('CLI tool "pstotext" is required for .ps backend.')


def _get_file(f, **kwargs):
    return run('pstotext', '-', stdin=f).decode('utf8')


def _get_path(path, **kwargs):
    return run('pstotext', path).decode('utf8')
