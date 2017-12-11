from __future__ import absolute_import

from fulltext.backends import __html
from fulltext.util import run, assert_cmd_exists
from fulltext import BaseBackend


def cmd(path, **kwargs):
    cmd = ['hwp5proc', 'xml']
    cmd.extend([path])
    return cmd


def to_text_with_backend(html):
    return __html.handle_fobj(html)


class Backend(BaseBackend):

    def check(self, title):
        assert_cmd_exists('hwp5proc')

    def handle_path(self, path):
        out = self.decode(run(*cmd(path)))
        return to_text_with_backend(out)
