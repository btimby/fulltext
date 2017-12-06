from six import StringIO

from ExtractMsg import Message


def handle_path(path, **kwargs):
    text, m = StringIO(), Message(path)

    text.write(m.subject)
    text.write(u'\n\n')
    text.write(m.body)

    return text.getvalue()
