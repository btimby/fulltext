#sudo apt-get install tesseract-ocr
#sudo pip3 install pytesseract
#sudo apt-get install tesseract-ocr-[lang]

from fulltext.util import which
import pytesseract
from PIL import Image
import logging

LOGGER = logging.getLogger(__name__)

EXTENSIONS = ('jpg', 'jpeg', 'bmp', 'png', 'gif')

if which('tesseract') is None:
    LOGGER.warning('CLI tool "tesseract" is required for image files backend.')

def read(img, **kargs):
    lang = kargs.get('lang', 'eng')

    im = Image.open(img)

    degree = 0
    try:
        exif = im._getexif()
    except AttributeError:
        exif = None

    if exif:
        orientation_key = 274 # cf ExifTags
        if orientation_key in exif:
            orientation = exif[orientation_key]
            rotate_values = {
                3: 180,
                6: 270,
                8: 90
            }
            if orientation in rotate_values:
                # Rotate and save the picture
                degree = rotate_values[orientation]

    if degree:
        im = im.rotate(degree)

    return pytesseract.image_to_string(im, lang = lang)

    
def _get_file(path_or_file, **kwargs):
    return read(path_or_file, **kwargs)


_get_path = _get_file
