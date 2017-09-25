from __future__ import absolute_import

from fulltext.util import run


EXTENSIONS = ('rtf', )


def _get_file(f, **kwargs):
    text = run('unrtf', '--text', '--nopict', stdin=f)
    return text.partition(b'-----------------')[2].decode('utf8')


def _get_path(path, **kwargs):
    text = run('unrtf', '--text', '--nopict', path)
    return text.partition(b'-----------------')[2].decode('utf8')
