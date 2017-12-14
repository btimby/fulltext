from __future__ import absolute_import

import contextlib
import os
import tempfile
import subprocess
import socket
import time

from fulltext.backends.__html import Backend as HTMLBackend
from fulltext import BaseBackend
from fulltext.util import assert_cmd_exists
from fulltext.util import run


SERVER_TIMEOUT = 3
SERVER_PORT = 2002
TRAVIS = bool(os.environ.get('TRAVIS'))


def connect_to_server(timeout):
    if not timeout:
        with contextlib.closing(socket.socket()) as s:
            return s.connect(("localhost", SERVER_PORT))

    stop_at = time.time() + timeout
    while time.time() < stop_at:
        with contextlib.closing(socket.socket()) as s:
            try:
                return s.connect(("localhost", SERVER_PORT))
            except socket.error:
                continue
    raise ValueError("timed out (can't connect to unoconv server)")


@contextlib.contextmanager
def get_server():
    try:
        # The listener may already be running.
        connect_to_server(timeout=None)
        yield
    except socket.error:
        # If not we start it, then connect() with a timeout.
        proc = subprocess.Popen("unoconv -l", shell=True)
        try:
            connect_to_server(SERVER_TIMEOUT)
            yield
        finally:
            proc.terminate()
            proc.wait()


class Backend(BaseBackend):

    def check(self, title):
        assert_cmd_exists('unoconv')

    def setup(self):
        self.html_backend = HTMLBackend(
            self.encoding, self.encoding_errors, self.kwargs)

    def handle_path(self, path):
        with get_server():
            fd, tfile = tempfile.mkstemp(suffix='.html')
            try:
                run("unoconv", "-d", "presentation",
                    "-o", tfile, "-f", "html", path)
                with open(tfile, 'rb') as f:
                    return self.html_backend.handle_fobj(f)
            finally:
                os.close(fd)
                os.remove(tfile)

    def handle_title(self, path):
        return self.html_backend.handle_title(path)
