import docx2txt


# Note: docx2txt does not support encoding.
def handle_fobj(path_or_file, **kwargs):
    return docx2txt.process(path_or_file)


# They are equivalent, process() uses zipfile.ZipFile().
handle_path = handle_fobj
