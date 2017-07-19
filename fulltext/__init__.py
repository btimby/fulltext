from __future__ import absolute_import

import re
import logging
import os
import shutil
import tempfile

from os.path import (
    basename, splitext
)


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

FULLTEXT_TEMP = os.environ.get('FULLTEXT_TEMP', tempfile.gettempdir())
STRIP_WHITE = re.compile(r'[ \t\v\f\r\n]+')
SENTINAL = object()


class BackendError(AssertionError):
    pass


class MissingCommandException(AssertionError):
    pass


def _get_path(backend, path, **kwargs):
    if callable(getattr(backend, '_get_file', None)):
        # Prefer _get_file(), if implemented.
        with open(path, 'rb') as f:
            return backend._get_file(f, **kwargs)

    elif callable(getattr(backend, '_get_path', None)):
        return backend._get_path(path, **kwargs)

    else:
        BackendError('Backend must provide `_get_path()` or `_get_file()`')


def _get_file(backend, f, **kwargs):
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
    if not name:
        name = getattr(path_or_file, 'name', None)

    if not name and isinstance(path_or_file, (str, unicode)):
        name = basename(path_or_file)

    try:
        backend_name = kwargs['backend']
    except KeyError:
        if name:
            ext = splitext(name)[1].lstrip('.')
        elif mime:
            ext = mime.partition('/')[2]
        else:
            ext = ''
        backend_name = ext.replace('-', '_')

    try:
        backend = getattr(
                __import__('fulltext.be', locals(), globals(), [backend_name]),
                backend_name)
    except (ImportError, AttributeError):
        LOGGER.warning('Could not load backend %s, using text', backend_name)
        backend = __import__('fulltext.be', locals(), globals(), ['text']).text

    kwargs['ext'] = ext

    try:
        if isinstance(path_or_file, (str, unicode)):
            if not name:
                name = basename(path_or_file)

            text = _get_path(backend, path_or_file, mime=mime, name=name, **kwargs)

        else:
            text = _get_file(backend, path_or_file, mime=mime, name=name, **kwargs)

    except Exception as e:
        LOGGER.exception(e)
        if default is not SENTINAL:
            return default
        raise

    else:
        return STRIP_WHITE.sub(' ', text).strip()
