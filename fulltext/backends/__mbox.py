import contextlib
import mailbox

from six import StringIO

from fulltext.backends.__eml import handle_fobj
from fulltext.util import BaseBackend


class Backend(BaseBackend):

    def handle_path(self, path):
        text, mb = StringIO(), mailbox.mbox(path, create=False)
        with contextlib.closing(mb):
            for k in mb.keys():
                t = handle_fobj(mb.get_file(k), self.encoding,
                                self.encoding_errors)
                text.write(t)
                text.write(u'\n\n')

        return text.getvalue()
