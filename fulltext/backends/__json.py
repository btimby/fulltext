import json
import sys

from six import StringIO
from six import string_types
from six import integer_types
from fulltext import BaseBackend


SCALAR_TYPES = string_types + integer_types
ENCODING = sys.getfilesystemencoding()


def to_text(text, obj):
    if isinstance(obj, dict):
        for key in sorted(obj.keys()):
            to_text(text, key)
            to_text(text, obj[key])

    elif isinstance(obj, list):
        for item in obj:
            to_text(text, item)

    elif isinstance(obj, SCALAR_TYPES):
        text.write(u'%s ' % obj)

    else:
        raise ValueError('Unrecognized type: %s' % obj.__class__)


class Backend(BaseBackend):

    def handle_fobj(self, f):
        text, data = StringIO(), f.read()

        # TODO: catch exception and attempt to use regex to strip formatting.
        obj = json.loads(self.decode(data))

        to_text(text, obj)

        return text.getvalue()
