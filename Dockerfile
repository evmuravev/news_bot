FROM python:3.11-slim-buster
WORKDIR /bot
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV PYTHONPATH /bot

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql python-psycopg2 libpq-dev\
  && apt-get clean

# install python dependencies
COPY ./requirements.txt /bot
RUN pip install --upgrade pip \
  && pip install -r requirements.txt
  
# RUN chmod +x /bot/main.py

# CMD python /bot/main.py;