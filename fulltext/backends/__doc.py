from __future__ import absolute_import

import logging

from fulltext.util import run, ShellError, MissingCommandException, warn
from fulltext.compat import which


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


if which('antiword') is None:
    warn('CLI tool "antiword" is required for .doc backend.')

if which('abiword') is None:
    warn('CLI tool "abiword" is optional for .doc backend.')


def _get_file(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    try:
        return run('antiword', '-', stdin=f).decode(encoding, errors)
    except ShellError as e:
        if b'not a Word Document' not in e.stderr:
            raise
        LOGGER.warning('.doc file unsupported format, trying abiword')
    except MissingCommandException:
        LOGGER.warning('CLI tool "antiword" missing, using "abiword"')

    f.seek(0)

    # Try abiword, slower, but supports more formats.
    return run(
        'abiword', '--to=txt', '--to-name=fd://1', 'fd://0', stdin=f
    ).decode(encoding, errors)


def _get_path(path, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    try:
        return run('antiword', path).decode(encoding, errors)
    except ShellError as e:
        if b'not a Word Document' not in e.stderr:
            raise
        LOGGER.warning('.doc file unsupported format, trying abiword')
    except MissingCommandException:
        LOGGER.warning('CLI tool "antiword" missing, using "abiword"')

    # Try abiword, slower, but supports more formats.
    return run('abiword', '--to=txt', '--to-name=fd://1', path).decode(
        encoding, errors)
