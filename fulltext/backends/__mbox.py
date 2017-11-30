import mailbox

from six import StringIO

from fulltext.backends.__eml import _get_file

def _get_path(path, **kwargs):
    text, mb = StringIO(), mailbox.mbox(path, create=False)

    for k in mb.keys():
        text.write(_get_file(mb.get_file(k)))
        text.write(u'\n\n')

    return text.getvalue()