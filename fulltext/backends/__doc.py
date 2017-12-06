from __future__ import absolute_import

import logging

from fulltext.util import run, ShellError, MissingCommandException
from fulltext.util import assert_cmd_exists


def check():
    assert_cmd_exists('antiword')
    assert_cmd_exists('abiword')


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def handle_fobj(f, **kwargs):
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


def handle_path(path, **kwargs):
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
