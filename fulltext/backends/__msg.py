from six import StringIO

from ExtractMsg import Message
from fulltext import BaseBackend


class Backend(BaseBackend):

    def handle_path(self, path):
        text, m = StringIO(), Message(path)

        text.write(m.subject)
        text.write(u'\n\n')
        text.write(m.body)

        return text.getvalue()
