###########
# BUILDER #
###########

# pull official base image
FROM python:3.10-alpine as builder

# set work directory
WORKDIR /digital-archive-server

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libxml2-dev libxslt-dev g++ libc-dev make zlib-dev jpeg-dev

RUN pip install --upgrade pip

COPY . .

# install dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /digital-archive-server/wheels -r requirements.txt

#########
# FINAL #
#########
FROM python:3.10-alpine

RUN mkdir /home/digital-archive-server

RUN addgroup -S archive && adduser -S archive -G archive

ENV HOME=/home/digital-archive-server
WORKDIR $HOME
RUN mkdir $HOME/static

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk update && apk add libpq libxml2-dev libxslt-dev g++ libc-dev ffmpeg
COPY --from=builder /digital-archive-server/wheels /wheels
COPY --from=builder /digital-archive-server/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $HOME/entrypoint.sh
RUN chmod +x  $HOME/entrypoint.sh

COPY . $HOME

RUN chown -R archive:archive $HOME
RUN chown -R archive:archive $HOME/static

USER archive

ENTRYPOINT ["/home/digital-archive-server/entrypoint.sh"]
