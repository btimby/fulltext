import contextlib
import mailbox

from six import StringIO

from fulltext.backends.__eml import handle_fobj


def handle_path(path, **kwargs):
    text, mb = StringIO(), mailbox.mbox(path, create=False)
    with contextlib.closing(mb):
        for k in mb.keys():
            text.write(handle_fobj(mb.get_file(k), **kwargs))
            text.write(u'\n\n')

    return text.getvalue()
