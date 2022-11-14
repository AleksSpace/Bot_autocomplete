FROM python:latest

RUN mkdir -p /code
WORKDIR /code

COPY  . /code
RUN python3 -m pip install --upgrade pip && \
    pip3 install -r /code/requirements.txt --no-cache-dir

CMD python3 bot.py
