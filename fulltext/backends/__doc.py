from __future__ import absolute_import

import logging

from fulltext.util import run, which, ShellError, MissingCommandException


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

EXTENSIONS = ('doc', )

if which('antiword') is None:
    LOGGER.warning('CLI tool "antiword" is required for .doc backend.')

if which('abiword') is None:
    LOGGER.warning('CLI tool "abiword" is optional for .doc backend.')


def _get_file(f, **kwargs):
    try:
        return run('antiword', '-', stdin=f).decode('utf8')
    except ShellError as e:
        if b'not a Word Document' not in e.stderr:
            raise
        LOGGER.warning('.doc file unsupported format')
    except MissingCommandException:
        LOGGER.warning('CLI tool "antiword" missing, using "abiword"')

    f.seek(0)

    # Try abiword, slower, but supports more formats.
    return run(
        'abiword', '--to=txt', '--to-name=fd://1', 'fd://0', stdin=f
    ).decode('utf8')


def _get_path(path, **kwargs):
    try:
        return run('antiword', path).decode('utf8')
    except ShellError as e:
        if b'not a Word Document' not in e.stderr:
            raise
        LOGGER.warning('.doc file unsupported format')
    except MissingCommandException:
        LOGGER.warning('CLI tool "antiword" missing, using "abiword"')

    # Try abiword, slower, but supports more formats.
    return run('abiword', '--to=txt', '--to-name=fd://1', path).decode('utf8')
