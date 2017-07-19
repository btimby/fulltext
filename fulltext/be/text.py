import sys

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


BUFFER_MAX = 8192
ENCODING = sys.getfilesystemencoding()


def _get_file(f, **kwargs):
    buffer = StringIO()
    enc = kwargs.get('enc', ENCODING)

    while True:
        text = f.read(BUFFER_MAX)

        if not text:
            break

        text = text.decode(enc, 'replace')

        buffer.write(text)

    return buffer.getvalue()
