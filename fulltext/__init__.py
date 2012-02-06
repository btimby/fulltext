import os, os.path, subprocess, re, csv, time, select, mimetypes
# TODO: support file-like objects (pipe file data to stdin).

mimetypes.add_type('application/rar', '.rar')

PROG_MAP = {
    (None, None): ('cat', '{0}'),
    ('application/pdf', None): ('pdftotext', '-q', '-nopgbrk', '{0}', '-'),
    ('application/msword', None): ('antiword', '{0}'),
    ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', None): ('docx2txt', '{0}', '-'),  # http://sourceforge.net/projects/docx2txt/
    ('application/vnd.ms-excel', None): ('convertxls2csv', '-q', '-x {0}', '-c -'),
    ('application/rtf', None): ('unrtf', '--text', '--nopict', '{0}'),
    ('application/vnd.oasis.opendocument.text', None): ('odt2txt', '{0}'),
    ('application/vnd.oasis.opendocument.spreadsheet', None): ('odt2txt', '{0}'),
    ('application/zip', None): ('zipinfo', '-2z', '{0}'),
    ('application/x-tar', 'gzip'): ('tar', 'tzf', '{0}'),
    ('application/x-tar', 'gzip2'): ('tar', 'tjf', '{0}'),
    ('application/rar', None): ('unrar', 'vb', '-p-', '-ierr', '-y', '{0}'),
    ('text/html', None): ('html2text', '-nobs', '{0}'),
    ('text/xml', None): ('html2text', '-nobs', '{0}'),
    ('image/jpeg', None): ('exiftool', '-s', '-s', '-s', '{0}'),
    ('video/mpeg', None): ('exiftool', '-s', '-s', '-s', '{0}'),
    ('audio/mpeg', None): ('exiftool', '-s', '-s', '-s', '{0}'),
    ('application/octet-stream', None): ('strings', '-n 18', '{0}'),
}

STRIP_WHITE = re.compile(r'[ \t\v\f\r\n]+')
UNRTF = re.compile(r'.*-+\n', flags=re.MULTILINE)

PROC_TIMEOUT     = 5
"How long to wait for command exectuion."

def strip_unrtf_header(text):
    """
    Can't find a way to turn off the stupid header in unrtf.
    """
    return text.split('-----------------')[1]

def csv_to_text(text):
    """
    Can convert xls to csv, but this will go from csv to plain old
    text.
    """
    buffer = []
    for row in csv.reader(text.splitlines(), dialect="excel"):
        buffer.append(' '.join(row))
    return ' '.join(buffer)

FUNC_MAP = {
    ('application/rtf', None): strip_unrtf_header,
    ('application/vnd.ms-excel', None): csv_to_text,
}

class FullTextException(Exception):
    pass


# From:
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def add_type(mime, command, encoding=None):
    assert isinstance(command, tuple), 'Command must be tuple.'
    assert '{0}' in command, 'Command must contain {0}.'
    PROG_MAP[(mime, encoding)] = command


def get_type(filename):
    return mimetypes.guess_type(filename)


def get(filename, default=None, type=None):
    # TODO: allow an open file to be passed in, most of the tools
    # can accept data from stdin.
    if not os.path.exists(filename):
        if default is not None:
            return default
        raise FullTextException('File not found')
    if type is None:
        type = get_type(filename)
    try:
        cmd = PROG_MAP[type]
    except KeyError:
        if default is not None:
            return default
        raise FullTextException('Unknown file type, known file types are: {0}'.format(' '.join(PROG_MAP.keys())))
    cmd = map(lambda x: x.format(filename), cmd)
    if which(cmd[0]) is None:
        raise FullTextException('Cannot execute binary: {0}'.format(cmd[0]))
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        f = p.stdout.fileno()
        s, b = time.time(), []
        while True:
            if time.time() - s >= PROC_TIMEOUT:
                p.stdout.close()
                p.terminate()
                raise FullTextException('Timeout executing command.')
            if f in select.select([f], [], [], 0)[0]:
                b.append(p.stdout.read())
            if p.poll() is not None:
                break
            time.sleep(0.1)
        text = ''.join(b)
    except:
        if default is not None:
            return default
        raise
    post = FUNC_MAP.get(type, None)
    if post:
        text = post(text)
    return STRIP_WHITE.sub(' ', text).strip()


def check():
    commands = {}
    for type, cmd in PROG_MAP.items():
        commands[cmd[0]] = None
    for cmd in commands.keys():
        if which(cmd) is None:
            print 'Cannot execute command {0}, please install it.'.format(cmd)
