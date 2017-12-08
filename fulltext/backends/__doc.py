from __future__ import absolute_import

import logging
import os

from fulltext.util import run, ShellError, MissingCommandException
from fulltext.util import assert_cmd_exists
from fulltext import BaseBackend
from fulltext.util import exiftool_title


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Backend(BaseBackend):

    def check(self):
        assert_cmd_exists('antiword')
        assert_cmd_exists('abiword')
        if "FULLTEXT_TESTING" in os.environ:
            assert_cmd_exists('pdfinfo')

    def handle_fobj(self, f):
        try:
            return self.decode(run('antiword', '-', stdin=f))
        except ShellError as e:
            if b'not a Word Document' not in e.stderr:
                raise
            LOGGER.warning('.doc file unsupported format, trying abiword')
        except MissingCommandException:
            LOGGER.warning('CLI tool "antiword" missing, using "abiword"')

        f.seek(0)

        # Try abiword, slower, but supports more formats.
        return self.decode(run(
            'abiword', '--to=txt', '--to-name=fd://1', 'fd://0', stdin=f
        ))

    def handle_path(self, path):
        try:
            return self.decode(run('antiword', path))
        except ShellError as e:
            if b'not a Word Document' not in e.stderr:
                raise
            LOGGER.warning('.doc file unsupported format, trying abiword')
        except MissingCommandException:
            LOGGER.warning('CLI tool "antiword" missing, using "abiword"')

        # Try abiword, slower, but supports more formats.
        return self.decode(
            run('abiword', '--to=txt', '--to-name=fd://1', path))

    def handle_title(self, f):
        return exiftool_title(f, self.encoding, self.encoding_errors)
