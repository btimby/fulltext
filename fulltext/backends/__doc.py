from __future__ import absolute_import

import logging

from fulltext.util import run, which


LOGGER = logging.getLogger(__name__)
EXTENSIONS = ('doc', )


if which('antiword') is None:
    LOGGER.warning('CLI tool "antiword" is required for .doc backend.')


def _get_file(f, **kwargs):
    return run('antiword', '-', stdin=f).decode('utf8')


def _get_path(path, **kwargs):
    return run('antiword', path).decode('utf8')
