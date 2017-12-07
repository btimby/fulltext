from email import message_from_file

import codecs

from six import StringIO
from fulltext import BaseBackend


# This is used by other modules, hence it's here.
def handle_fobj(f, encoding, errors):
    text = StringIO()
    encf = codecs.getreader(encoding)(f, errors=errors)
    m = message_from_file(encf)

    for part in m.walk():
        if part.get_content_type().startswith('text/plain'):
            text.write(part.get_payload())

    return text.getvalue()


class Backend(BaseBackend):

    def handle_fobj(self, f):
        return handle_fobj(f, self.encoding, self.encoding_errors)
