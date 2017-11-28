from __future__ import absolute_import

import logging
from fulltext.backends import __html
from fulltext.util import run, which, warn


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

EXTENSIONS = ('hwp',)


if which('hwp5proc') is None:
    warn('CLI tool "hwp5proc" is required for .hwp backend. use '
         '"pip2 install --pre pyhwp"')


def _cmd(path, **kwargs):
    cmd = ['hwp5proc', 'xml']
    cmd.extend([path])
    return cmd


def to_text_with_backend(html):
    return __html._get_file(html)


def _get_path(path, **kwargs):
    return to_text_with_backend(run(*_cmd(path, **kwargs)).decode('utf-8'))
