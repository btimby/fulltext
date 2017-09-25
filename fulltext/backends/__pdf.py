from __future__ import absolute_import

from fulltext.util import run


EXTENSIONS = ('pdf', )


def _get_file(f, **kwargs):
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend(['-', '-'])

    return run(*cmd, stdin=f)


def _get_path(path, **kwargs):
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend([path, '-'])

    return run(*cmd)
