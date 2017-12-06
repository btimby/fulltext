from __future__ import absolute_import

import csv

from six import StringIO
from six import PY3


if PY3:
    def readlines(f, encoding, errors):
        for line in f.readlines():
            yield line.decode(encoding, errors)

else:
    def unicode_reader(f, encoding, encoding_errors, **opts):
        reader = csv.reader(f, **opts)
        for row in reader:
            yield [unicode(cell, encoding, encoding_errors)  # NOQA
                   for cell in row]


def handle_fobj(f, **kwargs):
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

    if PY3:
        gen = readlines(f, encoding, errors)
        reader = csv.reader(gen, **options)
    else:
        reader = unicode_reader(f, encoding, errors, **options)

    text = StringIO()
    for row in reader:
        text.write(u' '.join(row))
        text.write(u'\n')

    return text.getvalue()
