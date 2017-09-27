from __future__ import absolute_import

import logging

from fulltext.util import run, which


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

EXTENSIONS = ('rtf', )


if which('unrtf') is None:
    LOGGER.warning('CLI tool "unrtf" is required for .rtf backend.')


def _strip(text):
    return text.partition(b'-----------------')[2].decode('utf8')


def _get_file(f, **kwargs):
    return _strip(run('unrtf', '--text', '--nopict', stdin=f))


def _get_path(path, **kwargs):
    return _strip(run('unrtf', '--text', '--nopict', path))
