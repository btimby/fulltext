from mobi import Mobi

from six import StringIO


def _get_path(path, **kwargs):
    text = StringIO()

    with Mobi(path) as book:
        for record in book:
            text.write(record.decode('utf8'))

    return text.getvalue()
