import mailbox

from six import StringIO


def _get_file(f, **kwargs):
    text = StringIO()
