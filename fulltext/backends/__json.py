import json
import sys

from six import StringIO
from six import string_types
from six import integer_types


SCALAR_TYPES = string_types + integer_types
ENCODING = sys.getfilesystemencoding()


def _to_text(text, obj):
    if isinstance(obj, dict):
        for key in sorted(obj.keys()):
            _to_text(text, key)
            _to_text(text, obj[key])

    elif isinstance(obj, list):
        for item in obj:
            _to_text(text, item)

    elif isinstance(obj, SCALAR_TYPES):
        text.write(u'%s ' % obj)

    else:
        raise ValueError('Unrecognized type: %s' % obj.__class__)


def _get_file(f, **kwargs):
    encoding = kwargs.get('encoding', ENCODING)
    text, data = StringIO(), f.read()

    # TODO: catch exception and attempt to use regex to strip formatting.
    obj = json.loads(data.decode(encoding))

    _to_text(text, obj)

    return text.getvalue()
