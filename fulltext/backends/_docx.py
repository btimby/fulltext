import docx2txt


EXTENSIONS = ('docx', )


def _get_file(path_or_file, **kwargs):
    return docx2txt.process(path_or_file)


# They are equivalent, process() uses zipfile.ZipFile().
_get_path = _get_file
