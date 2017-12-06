from __future__ import absolute_import
from fulltext.util import run, assert_cmd_exists


def check():
    assert_cmd_exists('pdftotext')


def cmd(path, **kwargs):
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend([path, '-'])

    return cmd


def handle_fobj(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    return run(*cmd('-', **kwargs), stdin=f).decode(encoding, errors)


def handle_path(path, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    return run(*cmd(path, **kwargs)).decode(encoding, errors)
