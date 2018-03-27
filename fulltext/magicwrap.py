import os

import puremagic

from fulltext.compat import WINDOWS
from fulltext.mimewrap import DEFAULT_MIME
from fulltext.mimewrap import ext_to_mimetype

if os.name == 'posix':
    import magic as _magic  # NOQA


def _mime_from_fname(fname):
    ext = os.path.splitext(fname)[1]
    if ext:
        # If we have an extension don't use magic and rely on our
        # internal mapping instead.
        return ext_to_mimetype(ext)


class MagicWrapper:

    @staticmethod
    def from_file(fname, mime=True):
        if not mime:
            raise ValueError("mime=False arg is not supported")
        ret = _mime_from_fname(fname)
        if not ret:
            ret = _magic.from_file(fname, mime=True)
        return ret

    @staticmethod
    def from_buffer(header, mime=True):
        if not mime:
            raise ValueError("mime=False arg is not supported")
        return _magic.from_buffer(header, mime=True)


class PuremagicWrapper:

    @staticmethod
    def _is_html(header):
        return header[:50].strip().lower().startswith(b"<!doctype html")

    @staticmethod
    def _guess_it(header):
        if PuremagicWrapper._is_html(header):
            return "text/html"
        return DEFAULT_MIME

    @staticmethod
    def from_file(fname, mime=True):
        if not mime:
            raise ValueError("mime=False arg is not supported")
        ret = _mime_from_fname(fname)
        if not ret:
            try:
                ret = puremagic.from_file(fname, mime=mime)
            except puremagic.PureError:
                return DEFAULT_MIME
            else:
                if not ret:
                    ret = DEFAULT_MIME
        return ret

    @staticmethod
    def from_buffer(header, mime=True):
        if not mime:
            raise ValueError("mime=False arg is not supported")
        try:
            ret = puremagic.from_string(header, mime=True)
        except puremagic.PureError:
            ret = PuremagicWrapper._guess_it(header)
        else:
            if not ret:
                ret = PuremagicWrapper._guess_it(header)
        if ret == "application/octet-stream":
            ret = PuremagicWrapper._guess_it(header)
        return ret


if WINDOWS:
    magic = PuremagicWrapper()
else:
    magic = MagicWrapper()


# =====================================================================
# Old implementation importing libmagic on Windows. This is commented
# out as libmagic.dll does not work on Python 32 bit so we rely on
# puremagic instead.
# =====================================================================

# def _import_magic():
#     # Instantiate our own Magic instance so we can tell it where the
#     # magic file lives.
#     from magic import Magic as _Magic

#     class Magic(_Magic):
#         # Overridden because differently from the UNIX version
#         # the Windows version does not provide mime kwarg.
#         def from_file(self, filename, mime=True):
#             return _Magic.from_file(self, filename)

#         def from_buffer(self, buf, mime=True):
#             return _Magic.from_buffer(self, buf)

#     path = pathjoin(get_bin_dir(), 'magic')
#     assert os.path.isfile(path), path
#     return Magic(mime=True, magic_file=path)

# magic = _import_magic()
