#!/bin/env python

from distutils.core import setup

name = 'fulltext'
version = '0.2'
release = '1'
versrel = version + '-' + release
download_url = 'https://github.com/downloads/btimby/' + name + \
                           '/' + name + '-' + versrel + '.tar.gz'
description = """\
A `SmartFile`_ Open Source project. `Read more`_ about how SmartFile
uses and contributes to Open Source software.

.. figure:: http://www.smartfile.com/images/logo.jpg
   :alt: SmartFile

Introduction
------------

Fulltext is meant to be used for full-text indexing of file contents for
search applications.

Fulltext is a library that makes converting various file formats to
plain text simple. Mostly it is a wrapper around shell tools. It will
execute the shell program, scrape it's results and then post-process the
results to pack as much text into as little space as possible.

Supported formats
-----------------

The following formats are supported using the command line apps listed.

-  application/pdf: pdftotext
-  application/msword: antiword
-  application/vnd.openxmlformats-officedocument.wordprocessingml.document:
   docx2txt
-  application/vnd.ms-excel: convertxls2csv
-  application/rtf: unrtf
-  application/vnd.oasis.opendocument.text: odt2txt
-  application/vnd.oasis.opendocument.spreadsheet: odt2txt
-  application/zip: funzip
-  application/x-tar, gzip: tar & gunzip
-  application/x-tar, bzip2: tar & bunzip2
-  application/rar: unrar
-  text/html: html2text
-  text/xml: html2text
-  image/jpeg: exiftool
-  video/mpeg: exiftool
-  audio/mpeg: exiftool
-  application/octet-stream: strings

Usage
-----

To use the library, simply pass a filename to the ``.get()`` module
function. A second optional argument ``default`` can provide a string to
be returned in case of error. This way, if you are not concerned with
exceptions, you can simply ignore them by providing a default. This is
like how the ``dict.get()`` method works.

::

    > import fulltext
    > fulltext.get('missing_file.pdf', '< no content >')
    '< no content >'
    > fulltext.get('existing.pdf', '< no content >'')
    'Lorem ipsum...'

There is also a quick way to check for the existence of all of the
required tools.

::

    > import fulltext
    > fulltext.check()
    Cannot execute command docx2txt, please install it.

Post-processing
---------------

Some formats require additional care, this is done in the
post-processing step. For example, unrtf is the tool used to convert
.rtf files to text. It prints a banner including the program version and
some document metadata. This header is removed in post-processing.

All receive some post-processing. The textwrap library is used to
perform some cleanup of the text. Then a regular expression is used to
condense any adjacent whitespace into a single space. Line breaks are
also removed in this step.

This results in the highest word-per-byte ratio possible, allowing your
full-text engine to quickly index the file contents.

Future
------

Sometimes multiple tools can be used. For example, catdoc provides
xls2csv, while xls2csv provides convertxls2csv. We should use whichever
is present.

I would like to do away with commands as tuples, and simply use strings.
This is something `easyprocess`_ can do.

.. _SmartFile: http://www.smartfile.com/
.. _Read more: http://www.smartfile.com/open-source.html
.. _easyprocess: http://pypi.python.org/pypi/EasyProcess
"""


setup(
    name = name,
    version = versrel,
    description = 'Convert binary files to plain text for indexing.',
    long_description = description,
    author = 'Ben Timby',
    author_email = 'btimby@gmail.com',
    maintainer = 'Ben Timby',
    maintainer_email = 'btimby@gmail.com',
    url = 'http://github.com/btimby/' + name + '/',
    download_url = download_url,
    license = 'GPLv3',
    packages = ["fulltext"],
    classifiers = (
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing :: Indexing',
    ),
)
