from __future__ import absolute_import

import csv

from six import StringIO


def readlines(f):
    for line in f.readlines():
        yield line.decode('utf8')


def _get_file(f, **kwargs):
    csv_kwargs = {
        'dialect': 'excel',
        'delimiter': ',',
    }

    mimetype = kwargs.get('mimetype', None)

    if mimetype == 'text/tsv':
        csv_kwargs = {
            'delimiter': '\t',
        }
    elif mimetype == 'text/psv':
        csv_kwargs = {
            'delimiter': '|',
        }

    text = StringIO()
    for row in csv.reader(readlines(f), **csv_kwargs):
        text.write(u' '.join(row))
        text.write(u'\n')
    return text.getvalue()
