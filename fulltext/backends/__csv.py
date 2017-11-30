from __future__ import absolute_import

import csv

from six import StringIO


def readlines(f):
    for line in f.readlines():
        yield line.decode('utf8')


def _get_file(f, **kwargs):
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
    for row in csv.reader(readlines(f), **options):
        text.write(u' '.join(row))
        text.write(u'\n')
    return text.getvalue()
