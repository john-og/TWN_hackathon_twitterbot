FROM python:3.7

WORKDIR /app


RUN pip install --upgrade pip && \
    pip install tweepy && \
    pip install nltk

RUN python -m nltk.downloader vader_lexicon

ADD twitterBot.py /app

ENTRYPOINT ["python3", "twitterBot.py"]
