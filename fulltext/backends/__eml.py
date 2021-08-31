from email import message_from_bytes

from six import StringIO
from fulltext.util import BaseBackend


# This is used by other modules, hence it's here.
def handle_fobj(f, encoding, errors):
    text = StringIO()
    m = message_from_bytes(f.read())
    for part in m.walk():
        if part.get_content_type().startswith('text/plain'):
            text.write(part.get_payload(decode=True).decode(encoding, errors=errors))  # noqa
    return text.getvalue()


class Backend(BaseBackend):

    def handle_fobj(self, f):
        return handle_fobj(f, self.encoding, self.encoding_errors)
