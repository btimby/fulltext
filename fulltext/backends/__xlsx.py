from __future__ import absolute_import

import xlrd
from six import StringIO

from fulltext import BaseBackend
from fulltext.util import assert_cmd_exists, exiftool_title


class Backend(BaseBackend):

    def check(self, title):
        if title:
            assert_cmd_exists('exiftool')

    def handle_path(self, path):
        text = StringIO()
        wb = xlrd.open_workbook(path)
        for n in wb.sheet_names():
            ws = wb.sheet_by_name(n)
            for x in range(ws.nrows):
                for y in range(ws.ncols):
                    v = ws.cell_value(x, y)
                    if v:
                        if isinstance(v, (int, float)):
                            v = str(v)
                        text.write(v)
                        text.write(u' ')
                text.write(u'\n')
        return text.getvalue()

    def handle_title(self, f):
        return exiftool_title(f, self.encoding, self.encoding_errors)
