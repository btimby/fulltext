import os, os.path, subprocess, re, csv, time, select
# TODO: support plain text files. Just read their content.
# TODO: support file-like objects (pipe file data to stdin).
# TODO: use mimetypes library for figuring out file type.

PROG_MAP = {
    '.pdf':     ('/usr/bin/pdftotext', '-q', '-nopgbrk', '{0}', '-'),
    '.doc':     ('/usr/bin/antiword', '{0}'),
    '.docx':    ('/usr/local/bin/docx2txt', '{0}', '-'),  # http://sourceforge.net/projects/docx2txt/
    #'.xls':     '/usr/bin/xls2csv {0}',
    '.xls':     ('/usr/bin/convertxls2csv', '-q', '-x {0}', '-c -'),
    '.rtf':     ('/usr/bin/unrtf', '--text', '--nopict', '{0}'),
    '.odt':     ('/usr/bin/odt2txt', '{0}'),
    '.ods':     ('/usr/bin/odt2txt', '{0}'),
    '.zip':     ('/usr/bin/zipinfo', '-2z', '{0}'),
    '.tar.gz':  ('/bin/tar', 'tzf', '{0}'),
    '.tar.bz2': ('/bin/tar', 'tjf', '{0}'),
    '.rar':     ('/usr/bin/unrar', 'vb', '-p-', '-ierr', '-y', '{0}'),
    '.htm':     ('/usr/bin/html2text', '-nobs', '{0}'),
    '.html':    ('/usr/bin/html2text', '-nobs', '{0}'),
    '.xml':     ('/usr/bin/html2text', '-nobs', '{0}'),
    '.jpg':     ('/usr/bin/exiftool', '-s', '-s', '-s', '{0}'),
    '.jpeg':    ('/usr/bin/exiftool', '-s', '-s', '-s', '{0}'),
    '.mpg':     ('/usr/bin/exiftool', '-s', '-s', '-s', '{0}'),
    '.mpeg':    ('/usr/bin/exiftool', '-s', '-s', '-s', '{0}'),
    '.mp3':     ('/usr/bin/exiftool', '-s', '-s', '-s', '{0}'),
    '.dll':     ('/usr/bin/strings', '-n 18', '{0}'),
    '.exe':     ('/usr/bin/strings', '-n 18', '{0}'),
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
    '.rtf': strip_unrtf_header,
    '.xls': csv_to_text,
}

class FullTextException(Exception):
    pass


def get_type(filename):
    name, ext = os.path.splitext(filename)
    if ext in ('.gz', '.bz2') and name.endswith('.tar'):
        ext = '.tar' + ext
    if ext in PROG_MAP:
        return ext


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
    if not os.access(cmd[0], os.F_OK | os.X_OK):
        if default is not None:
            return default
        raise FullTextException('Cannot execute binary: {0}'.format(cmd[0]))
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    for type, cmd in PROG_MAP.items():
        if not os.access(cmd[0], os.F_OK | os.X_OK):
            print 'Cannot find converter for {0}, please install: {1}'.format(type, cmd[0])
    print 'All other converters present and accounted for.'
