from __future__ import absolute_import

import logging
from html2text import config
import html2text
from fulltext.util import run, which

config.BODY_WIDTH = 0

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

EXTENSIONS = ('hwp',)


if which('hwp5proc') is None:
    LOGGER.warning('CLI tool "hwp5proc" is required for .hwp backend. use "pip install pyhwp"')


def _cmd(path, **kwargs):
    cmd = ['hwp5proc', 'xml']
    cmd.extend([path])
    return cmd


def to_text(html):
    return html2text.html2text(html)


def _get_path(path, **kwargs):
    return to_text(run(*_cmd(path, **kwargs)).decode('utf-8'))
