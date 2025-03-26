FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/schedule_backend

COPY ./requirements.txt /usr/src/schedule_backend/requirements.txt
RUN env >> /etc/environment && apt-get update &&  \
    apt-get autoremove -y && \
    apt-get install --no-install-recommends -y cron libpq-dev nano &&  \
    pip install -r /usr/src/schedule_backend/requirements.txt


COPY ./ /usr/src/schedule_backend

EXPOSE 8000
