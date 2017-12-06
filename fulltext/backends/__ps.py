# To create a postscript file for test:
# enscript -B --word-wrap -ptest.ps test.txt

from __future__ import absolute_import
from fulltext.util import run, assert_cmd_exists


def test():
    assert_cmd_exists('pstotext')


def _get_file(f, **kwargs):
    out = run('pstotext', '-', stdin=f)
    return out.decode(kwargs['encoding'], kwargs['encoding_errors'])


def _get_path(path, **kwargs):
    out = run('pstotext', path)
    return out.decode(kwargs['encoding'], kwargs['encoding_errors'])
