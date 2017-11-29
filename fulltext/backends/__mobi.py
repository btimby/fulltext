from mobi import Mobi

from six import StringIO


def _get_path(path, **kwargs):
    text, book = StringIO(), Mobi(path)
    book.parse()

    for record in book:
        text.write(record)

    return text.getvalue()
