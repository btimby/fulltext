import contextlib
from six import StringIO

from ExtractMsg import Message
from fulltext.util import BaseBackend


class Backend(BaseBackend):

    def handle_path(self, path):
        text = StringIO()
        with contextlib.closing(Message(path)) as m:
            text.write(m.subject)
            text.write(u'\n\n')
            text.write(m.body)
        return text.getvalue()
