Introduction
----

Fulltext is meant to be used for full-text indexing of file contents for search applications.

Fulltext is a library that makes converting various file formats to plain text simple. Mostly
it is a wrapper around shell tools. It will execute the shell program, scrape it's results
and then post-process the results to pack as much text into as little space as possible.

Supported formats
----

The following formats are supported using the command line apps listed.

 *  .pdf: /usr/bin/pdftotext
 *  .doc: /usr/bin/antiword
 *  .docx: /usr/local/bin/docx2txt
 *  .xls: /usr/bin/convertxls2csv
 *  .rtf: /usr/bin/unrtf
 *  .odt: /usr/bin/odt2txt
 *  .ods: /usr/bin/odt2txt
 *  .zip: /usr/bin/zipinfo
 *  .tar.gz: /bin/tar
 *  .tar.bz2: /bin/tar
 *  .rar: /usr/bin/unrar
 *  .htm: /usr/bin/html2text
 *  .html: /usr/bin/html2text
 *  .xml: /usr/bin/html2text
 *  .jpeg: /usr/bin/exiftool
 *  .mpeg: /usr/bin/exiftool
 *  .mp3: /usr/bin/exiftool
 *  .dll: /usr/bin/strings
 *  .exe: /usr/bin/strings

Usage
----

To use the library, simply pass a filename to the `.get()`  module function. A second optional
argument `default` can provide a string to be returned in case of error. This way, if you are
not concerned with exceptions, you can simply ignore them by providing a default. This is like
how the `dict.get()` method works.

```python
> import fulltext
> fulltext.get('missing_file.pdf', '< no content >')
'< no content >'
> fulltext.get('existing.pdf', '< no content >'')
'Lorem ipsum...'
```

There is also a quick way to check for the existence of all of the required tools.

```bash
$ python fulltext/__init__.py
Cannot find converter for .xml, please install: /usr/bin/html2text
Cannot find converter for .mpeg, please install: /usr/bin/exiftool
Cannot find converter for .mpg, please install: /usr/bin/exiftool
Cannot find converter for .jpg, please install: /usr/bin/exiftool
Cannot find converter for .mp3, please install: /usr/bin/exiftool
Cannot find converter for .html, please install: /usr/bin/html2text
Cannot find converter for .docx, please install: /usr/local/bin/docx2txt
Cannot find converter for .htm, please install: /usr/bin/html2text
Cannot find converter for .jpeg, please install: /usr/bin/exiftool
All other converters present and accounted for.
```

Post-processing
----

Some formats require additional care, this is done in the post-processing step. For example, unrtf
is the tool used to convert .rtf files to text. It prints a banner including the program version
and some document metadata. This header is removed in post-processing.

All receive some post-processing. The textwrap library is used to perform some cleanup of the text.
Then a regular expression is used to condense any adjacent whitespace into a single space. Line breaks
are also removed in this step.

This results in the highest word-per-byte ratio possible, allowing your full-text engine to quickly index
the file contents.

Future
----

A feature to expect in the near future is support for file-like objects:

```python
> import fulltext
> f = file('existing.pdf', 'r')
> fulltext.get(f, '< no content >')
'Lorem ipsum...'
```