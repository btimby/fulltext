from __future__ import absolute_import

import csv

from six import StringIO
from six import PY3


if PY3:
    def unicode_reader(f, encoding, encoding_errors, **opts):
        def readlines(f):
            for line in f.readlines():
                yield line.decode(encoding, encoding_errors)

        return csv.reader(readlines(f), **opts)
else:
    def unicode_reader(f, encoding, encoding_errors, **opts):
        reader = csv.reader(f, **opts)
        for row in reader:
            yield [unicode(cell, encoding, encoding_errors)  # NOQA
                   for cell in row]


def _get_file(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    options = {
        'dialect': 'excel',
        'delimiter': ',',
    }

    mimetype = kwargs.get('mime', None)

    if mimetype == 'text/tsv':
        options['delimiter'] = '\t'

    elif mimetype == 'text/psv':
        options['delimiter'] = '|'

    text = StringIO()
    reader = unicode_reader(f, encoding, errors, **options)
    for row in reader:
        text.write(u' '.join(row))
        text.write(u'\n')

    return text.getvalue()
