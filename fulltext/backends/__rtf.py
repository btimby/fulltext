from __future__ import absolute_import

import logging

from fulltext.util import run, which


LOGGER = logging.getLogger(__name__)
EXTENSIONS = ('rtf', )


if which('unrtf') is None:
    LOGGER.warning('CLI tool "unrtf" is required for .rtf backend.')


def _get_file(f, **kwargs):
    text = run('unrtf', '--text', '--nopict', stdin=f)
    return text.partition(b'-----------------')[2].decode('utf8')


def _get_path(path, **kwargs):
    text = run('unrtf', '--text', '--nopict', path)
    return text.partition(b'-----------------')[2].decode('utf8')
