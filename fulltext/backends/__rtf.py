from __future__ import absolute_import
from fulltext.util import run
from fulltext.util import assert_cmd_exists


def test():
    assert_cmd_exists('unrtf')


def _strip(text, encoding, errors):
    return text.partition(b'-----------------')[2].decode(encoding, errors)


def handle_fobj(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    return _strip(run('unrtf', '--text', '--nopict', stdin=f),
                  encoding, errors)


def handle_path(path, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    return _strip(run('unrtf', '--text', '--nopict', path),
                  encoding, errors)
