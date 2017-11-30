import json

from six import StringIO
from six import string_types
from six import integer_types


def _to_text(text, obj):
    if isinstance(obj, dict):
        for key in sorted(obj.keys()):
            _to_text(text, key)
            _to_text(text, obj[key])

    elif isinstance(obj, list):
        for item in obj:
            _to_text(text, item)

    elif isinstance(obj, string_types):
        text.write(obj)
        text.write(u' ')

    elif isinstance(obj, integer_types):
        text.write(str(obj))
        text.write(u' ')


def _get_file(f, **kwargs):
    text, obj = StringIO(), json.loads(f.read().decode('utf8'))

    _to_text(text, obj)

    return text.getvalue()
