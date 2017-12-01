from __future__ import absolute_import

import csv

from six import StringIO


def readlines(f, encoding, errors):
    for line in f.readlines():
        yield line.decode(encoding, errors)


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
    gen = readlines(f, encoding, errors)
    for row in csv.reader(gen, **options):
        text.write(u' '.join(row))
        text.write(u'\n')
    return text.getvalue()
