from __future__ import absolute_import

import logging
from fulltext.backends import __html
from fulltext.util import run, warn
from fulltext.compat import which


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


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
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    return to_text_with_backend(run(*_cmd(path, **kwargs)).decode(
        encoding, errors))
