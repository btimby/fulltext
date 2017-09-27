from __future__ import absolute_import

import csv

from six import StringIO


EXTENSIONS = ('csv', )


def _get_file(f, **kwargs):
    text = StringIO()
    for row in csv.reader(f.readlines(), dialect='excel'):
        text.write(' '.join(row))
        text.write('\n')
    return text.getvalue()
