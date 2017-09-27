from __future__ import absolute_import

import re
import logging

from fulltext.util import run, which


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

EXTENSIONS = ('doc', )

# Antiword wraps our output, any single newline is wrapped, multiple newlines
# are preserved, and will be folded by fulltext later.
STRIP_EOL = re.compile(r'\r?\n')


if which('antiword') is None:
    LOGGER.warning('CLI tool "antiword" is required for .doc backend.')


def _get_file(f, **kwargs):
    return run('antiword', '-', stdin=f).decode('utf8')


def _get_path(path, **kwargs):
    return run('antiword', path).decode('utf8')
