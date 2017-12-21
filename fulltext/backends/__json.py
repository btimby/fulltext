import json
import sys
import re

from six import StringIO
from six import string_types
from six import integer_types
from fulltext import BaseBackend


STRIP_JSON = re.compile(r'[{}\'":\[\] ]+')
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
        text = StringIO()
        data = self.decode(f.read())

        try:
            obj = json.loads(data)

        except json.JSONDecodeError:
            # If the JSON is invalid, try to cheaply strip out the JSON-related
            # chars. In this case we don't need to recursively walk the object
            # since it is just a stripped string.
            text.write(STRIP_JSON.sub(' ', data))

        else:
            to_text(text, obj)

        return text.getvalue()
