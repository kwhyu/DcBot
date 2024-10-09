# Menggunakan base image Python versi 3.9
FROM python:3.9-slim

# Setel direktori kerja dalam container
WORKDIR /app

# Salin file requirements.txt untuk menginstal dependensi
COPY requirements.txt /app/requirements.txt

# Install dependencies Python yang dibutuhkan
RUN pip install -r /app/requirements.txt

# Install FFmpeg di container
RUN apt-get update && apt-get install -y ffmpeg

# Salin seluruh isi proyek ke dalam container
COPY . /app

# Perintah untuk menjalankan bot
CMD ["python", "main.py"]
