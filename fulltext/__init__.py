from __future__ import absolute_import

import re
import imp
import logging
import os
import glob
import shutil
import tempfile

from six import string_types

from os.path import join as pathjoin
from os.path import (
    basename, splitext, dirname
)


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

FULLTEXT_TEMP = os.environ.get('FULLTEXT_TEMP', tempfile.gettempdir())
FULLTEXT_PATH = os.environ.get('FULLTEXT_PATH', '')

STRIP_WHITE = re.compile(r'[ \t\v\f\r\n]+')
SENTINAL = object()
BACKENDS = {}


def _import_backends():
    paths = [pathjoin(dirname(__file__), 'backends')]
    if FULLTEXT_PATH:
        paths.extend(FULLTEXT_PATH.split(';'))

    for p in paths:
        for f in glob.iglob(pathjoin(p, '*.py')):
            name = splitext(basename(f))[0]
            module = imp.load_source(name, f)
            extensions = getattr(module, 'EXTENSIONS', (name, ))
            for ext in extensions:
                BACKENDS[ext] = module

    LOGGER.info('Loaded backends: %s', ', '.join(BACKENDS.keys()))


class BackendError(AssertionError):
    pass


class MissingCommandException(AssertionError):
    pass


def _get_path(backend, path, **kwargs):
    """
    Handle a path.

    Called by `get()` when provided a path. This function will prefer the
    backend's `_get_path()` if one is provided Otherwise, it will open the
    given path then use `_get_file()`.
    """
    if callable(getattr(backend, '_get_path', None)):
        return backend._get_path(path, **kwargs)

    elif callable(getattr(backend, '_get_file', None)):
        with open(path, 'rb') as f:
            return backend._get_file(f, **kwargs)

    else:
        BackendError('Backend must provide `_get_path()` or `_get_file()`')


def _get_file(backend, f, **kwargs):
    """
    Handle a file-like object.

    Called by `get()` when provided a file-like. This function will prefer the
    backend's `_get_file()` if one is provided. Otherwise, it will write the
    data to a temporary file and call `_get_path()`.
    """
    if callable(getattr(backend, '_get_file', None)):
        return backend._get_file(f, **kwargs)

    elif callable(getattr(backend, '_get_path', None)):
        LOGGER.warning("Using disk, backend does not provde `_get_file()`")

        ext = ''
        if 'ext' in kwargs:
            ext = '.' + kwargs['ext']

        with tempfile.NamedTemporaryFile(dir=FULLTEXT_TEMP, suffix=ext) as t:
            shutil.copyfileobj(f, t)
            t.flush()
            return backend._get_path(t.name, **kwargs)

    else:
        BackendError('Backend must provide `_get_path()` or `_get_file()`')


def get(path_or_file, default=SENTINAL, mime=None, name=None, **kwargs):
    """
    Get document full text.

    Accepts a path or file-like object. If given, `default` is returned
    instead of an error. `mime` and `name` should be passed if the information
    is available to caller, otherwise a best guess is made.
    """
    if not name:
        name = getattr(path_or_file, 'name', None)

    if not name and isinstance(path_or_file, string_types):
        name = basename(path_or_file)

    try:
        backend_name = kwargs.pop('backend')
    except KeyError:
        if name:
            ext = splitext(name)[1].lstrip('.')
        elif mime:
            ext = mime.partition('/')[2]
        else:
            ext = ''
        backend_name = ext.replace('-', '_').lower()

    if not backend_name in BACKENDS:
        LOGGER.warning('Falling back to text backend')
        backend_name = 'text'

    backend = BACKENDS[backend_name]

    try:
        if isinstance(path_or_file, string_types):
            if not name:
                name = basename(path_or_file)

            text = _get_path(
                backend, path_or_file, mime=mime, name=name, **kwargs)

        else:
            text = _get_file(
                backend, path_or_file, mime=mime, name=name, **kwargs)

    except Exception as e:
        LOGGER.exception(e)
        if default is not SENTINAL:
            return default
        raise

    else:
        return STRIP_WHITE.sub(' ', text).strip()


# Some backends use this module, so import them last.
_import_backends()
