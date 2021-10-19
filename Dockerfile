FROM python:alpine
ADD . /tootbot/
WORKDIR /tootbot
RUN pip3 install -r requirements.txt
VOLUME /tootbot

CMD python3 tootbot.py -c tootbot.ini
