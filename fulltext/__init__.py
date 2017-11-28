from __future__ import absolute_import

import re
import imp
import logging
import os
import glob
import shutil
import tempfile

from os.path import join as pathjoin
from os.path import (
    basename, splitext, dirname
)

from six import string_types
from six import PY3
from fulltext.util import warn


__all__ = ["get"]


LOGGER = logging.getLogger(__file__)
LOGGER.addHandler(logging.NullHandler())

FULLTEXT_TEMP = os.environ.get('FULLTEXT_TEMP', tempfile.gettempdir())
FULLTEXT_PATH = os.environ.get('FULLTEXT_PATH', '')

STRIP_WHITE = re.compile(r'[ \t\v\f]+')
STRIP_EOL = re.compile(r'[\r\n]+')
SENTINAL = object()
BACKENDS = {}


def _import_backends():
    paths = [pathjoin(dirname(__file__), 'backends')]

    if FULLTEXT_PATH:
        paths.extend(FULLTEXT_PATH.split(os.pathsep))

    for path in paths:
        for filename in glob.iglob(pathjoin(path, '*.py')):
            module_name = splitext(basename(filename))[0]
            try:
                module = imp.load_source(module_name, filename)
            except ImportError as e:
                warn('Backend %s disabled due to missing dependency; %s' % (
                    module_name, e.args[0]))
                continue

            has_get_path = callable(getattr(module, '_get_path', None))
            has_get_file = callable(getattr(module, '_get_file', None))
            if not (has_get_path or has_get_file):
                if module_name != '__init__':
                    # No worries, __init__ is part of a package, is often left
                    # empty.
                    LOGGER.warning(
                        'Backend %s defines neither `_get_path()` nor '
                        '`_get_file()`, disabled', module)
                continue

            extensions = getattr(
                module, 'EXTENSIONS', (module_name.lstrip('_'), ))

            for ext in extensions:
                if ext in BACKENDS:
                    LOGGER.warning('Backend %s overrides %s for %s',
                                   module, BACKENDS[ext], ext)
                BACKENDS[ext] = module

    LOGGER.info('Loaded backends: %s', ', '.join(BACKENDS.keys()))


def is_binary(f):
    """Return True if binary mode."""
    # Python 2 makes no distinction.
    if not PY3:
        return True

    # If the file has a mode, and it contains b, it is binary.
    if 'b' in getattr(f, 'mode', ''):
        return True

    # If it has a decoding attribute with a value, it is text mode.
    if getattr(f, "encoding", None):
        return False

    # Can we sniff?
    if not hasattr(f, 'seek'):
        return False
    # Finally, let's sniff by reading a byte.
    byte = f.read(1)
    f.seek(-1, os.SEEK_CUR)
    return hasattr(byte, 'decode')


def _get_path(backend, path, **kwargs):
    """
    Handle a path.

    Called by `get()` when provided a path. This function will prefer the
    backend's `_get_path()` if one is provided Otherwise, it will open the
    given path then use `_get_file()`.
    """
    if callable(getattr(backend, '_get_path', None)):
        # Prefer _get_path() if present.
        return backend._get_path(path, **kwargs)

    elif callable(getattr(backend, '_get_file', None)):
        # Fallback to _get_file(). No warning here since the performance hit
        # is minimal.
        with open(path, 'rb') as f:
            return backend._get_file(f, **kwargs)


def _get_file(backend, f, **kwargs):
    """
    Handle a file-like object.

    Called by `get()` when provided a file-like. This function will prefer the
    backend's `_get_file()` if one is provided. Otherwise, it will write the
    data to a temporary file and call `_get_path()`.
    """
    if not is_binary(f):
        raise AssertionError('File must be opened in binary mode.')

    if callable(getattr(backend, '_get_file', None)):
        # Prefer _get_file() if present.
        return backend._get_file(f, **kwargs)

    elif callable(getattr(backend, '_get_path', None)):
        # Fallback to _get_path(). Warn user since this is potentially
        # expensive.
        LOGGER.warning("Using disk, backend does not provide `_get_file()`")

        ext = ''
        if 'ext' in kwargs:
            ext = '.' + kwargs['ext']

        with tempfile.NamedTemporaryFile(dir=FULLTEXT_TEMP, suffix=ext) as t:
            shutil.copyfileobj(f, t)
            t.flush()
            return backend._get_path(t.name, **kwargs)


def get(path_or_file, default=SENTINAL, mime=None, name=None, backend=None,
        kwargs={}):
    """
    Get document full text.

    Accepts a path or file-like object.
    If given, `default` is returned instead of an error.
    `backend` is a string specifying which backend to use (e.g. "doc").
    `mime` and `name` should be passed if the information
    is available to caller, otherwise a best guess is made.
    `kwargs` are passed to the underlying backend.
    """
    if not name:
        name = getattr(path_or_file, 'name', None)

    if not name and isinstance(path_or_file, string_types):
        name = basename(path_or_file)

    if backend is None:
        if name:
            ext = splitext(name)[1].lstrip('.')
        elif mime:
            ext = mime.partition('/')[2]
        else:
            ext = ''
        backend = ext.replace('-', '_').lower()

    if backend not in BACKENDS:
        LOGGER.warning('Falling back to binary backend')
        backend_mod = BACKENDS['bin']
    else:
        backend_mod = BACKENDS[backend]

    fun = _get_path if isinstance(path_or_file, string_types) else _get_file
    try:
        text = fun(backend_mod, path_or_file, **kwargs)
    except Exception as e:
        LOGGER.exception(e)
        if default is not SENTINAL:
            return default
        raise
    else:
        text = STRIP_WHITE.sub(' ', text)
        text = STRIP_EOL.sub(' ', text)
        return text.strip()


# Some backends use this module, so import them last.
_import_backends()
