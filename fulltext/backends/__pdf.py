from __future__ import absolute_import

import logging

from fulltext.util import run, which


LOGGER = logging.getLogger(__name__)
EXTENSIONS = ('pdf', )


if which('pdftotext') is None:
    LOGGER.warning('CLI tool "pdftotext" is required for .pdf backend.')


def _get_file(f, **kwargs):
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend(['-', '-'])

    return run(*cmd, stdin=f)


def _get_path(path, **kwargs):
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend([path, '-'])

    return run(*cmd)
