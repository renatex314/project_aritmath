FROM python:3.13.3-bookworm

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 nginx -y

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY model_downloader.py ./
RUN python model_downloader.py

COPY nginx.conf /etc/nginx/nginx.conf
COPY . .

EXPOSE 80

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]