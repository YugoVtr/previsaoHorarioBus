FROM python:3

WORKDIR /usr/app

RUN pip install scrapy ipdb

COPY . . 

EXPOSE 3333
