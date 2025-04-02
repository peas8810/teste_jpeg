FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    poppler-utils \
    libreoffice \
    tesseract-ocr \
    libgl1 \
    && apt-get clean

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "app.py"]

