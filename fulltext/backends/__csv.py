from __future__ import absolute_import

import csv
import codecs

from six import StringIO


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

    text, f = StringIO(), codecs.getreader('utf8')(f, errors='ignore')

    for row in csv.reader(f.readlines(), **options):
        text.write(u' '.join(row))
        text.write(u'\n')

    return text.getvalue()
