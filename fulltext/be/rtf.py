from __future__ import absolute_import

import re
import tempfile

from fulltext.util import run


def _get_file(f, **kwargs):
    text = run('unrtf', '--text', '--nopict', stdin=f)
    return text.partition('-----------------')[2]


def _get_path(path, **kwargs):
    text = run('unrtf', '--text', '--nopict', path)
    return text.partition('-----------------')[2]
