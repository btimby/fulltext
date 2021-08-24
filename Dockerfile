# Assuems current working directory is root of fulltext.
FROM python:3.9.2

RUN apt-get update -y
RUN apt-get -y install antiword abiword unrtf poppler-utils libjpeg-dev # pstotext
RUN apt-get install -y tesseract-ocr tesseract-ocr-jpn libtesseract-dev libleptonica-dev tesseract-ocr-script-jpan tesseract-ocr-script-jpan-vert 

ENV HOME /home
WORKDIR $HOME

RUN apt-get update && \
    apt-get -y install antiword \
	libjpeg-dev \
	poppler-utils \
	tesseract-ocr abiword \
	unrtf \
	libimage-exiftool-perl \
	unrar-free

COPY . $HOME
RUN pip install -r $HOME/requirements.txt && pip install $HOME/.

#COPY . $HOME

EXPOSE 8000
EXPOSE 8080

CMD PYTHONWARNINGS=all FULLTEXT_TESTING=1 python fulltext/test/__init__.py 