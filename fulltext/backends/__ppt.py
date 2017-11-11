from __future__ import absolute_import

import os

import logging

import tempfile

from fulltext.util import run, which, ShellError, MissingCommandException

from fulltext.backends import __html

import fulltext

import time
import subprocess
import threading
import signal


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())
EXTENSIONS = ('ppt',)
UNOCONV_SERVER = None

if which('pdftotext') is None:
    LOGGER.warning('CLI tool "unoconv" is required for .ppt backend.')


def _run_server():
    global UNOCONV_SERVER
		
    UNOCONV_SERVER = subprocess.call("unoconv -l", shell=True)


def __start():
    if UNOCONV_SERVER is not None:
		    return
    threading.Thread(target = _run_server).start()
    # wait for server
    time.sleep(2)


def __shutdown():
    os.kill(UNOCONV_SERVER, signal.SIGTERM)


def _cmd(path, out, **kwargs):
    cmd = ['unoconv']

    cmd.extend(['-f', 'html', '-o', out, path])

    return cmd


def _get_temp():
    return os.path.join(fulltext.FULLTEXT_TEMP, next(tempfile._get_candidate_names()))


def _get_path(path, **kwargs):    		
		# unoconv's --stdout option doesn't work, why?
    out = _get_temp() + '.html'
    __start()
    try:
        r = run(*_cmd(path, out, **kwargs)).decode('utf-8')

    except ShellError as e:
        if b'UnoException' not in e.stderr:
            raise
        LOGGER.warning('unsupported format or corrupted file')

    except MissingCommandException:
        LOGGER.warning('CLI tool "unoconv" missing, using "unoconv"')

    r = ''
    if not os.path.isfile(out):
        LOGGER.warning('conversion failed')
        return r

    with open(out) as f:
        r = __html._get_file(f.read())

    os.remove(out)
    __shutdown
    return r.replace('\n', ' ')


def _get_file(f, **kwargs):
    # unoconv need file ext
    return _get_path(kwargs['name'])
