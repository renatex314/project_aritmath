FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY model_downloader.py ./
RUN python model_downloader.py

COPY . .

CMD ["python", "./main.py"]
