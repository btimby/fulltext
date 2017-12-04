from email import message_from_file

import codecs

from six import StringIO


def _get_file(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    text = StringIO()
    f2 = codecs.getreader(encoding)(f, errors=errors)
    m = message_from_file(f2)

    for part in m.walk():
        if part.get_content_type().startswith('text/plain'):
            text.write(part.get_payload())

    return text.getvalue()
