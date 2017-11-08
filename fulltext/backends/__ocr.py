# sudo apt-get install tesseract-ocr
# sudo pip3 install pytesseract
# sudo apt-get install tesseract-ocr-[lang]

from fulltext.util import which
import pytesseract
from PIL import Image
import logging

LOGGER = logging.getLogger(__name__)

EXTENSIONS = ('jpg', 'jpeg', 'bmp', 'png', 'gif')

EXIF_ORIENTATION = 274  # cf ExifTags

EXIF_ROTATION = {
    3: 180,
    6: 270,
    8: 90
}

if which('tesseract') is None:
    LOGGER.warning('CLI tool "tesseract" is required for image files backend.')


def read(img, **kargs):
    lang = kargs.get('lang', 'eng')
    rotate = kargs.get('rotate', 0)

    im = Image.open(img)

    if not rotate:
        try:
            exif = im._getexif()
        except AttributeError:
            # No EXIF data, no rotation necessary.
            pass
        else:
            rotate = EXIF_ROTATION.get(exif.get(EXIF_ORIENTATION, None), 0)

    if rotate:
        im = im.rotate(rotate)

    return pytesseract.image_to_string(im, lang=lang)


def _get_file(path_or_file, **kwargs):
    return read(path_or_file, **kwargs)


_get_path = _get_file
