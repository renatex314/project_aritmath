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
CMD [ \
    "bash", "-c", \ 
    "python", "/app/service1.py", "&", \
    "python", "/app/service2.py", "&", \
    "nginx", "-g", "'daemon off;'" \
]