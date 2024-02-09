FROM python:3.10-alpine

RUN apk --no-cache add  \
    bash \
    postgresql-client \
    gcc \
    linux-headers \
    build-base \
    python3-dev \
    libffi-dev \
    openssl-dev
#    musl-dev \
#    libpq-dev \
#    curl  \
#    rust \
#    cargo \
#    libuv \

COPY ./requirements.txt /src/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /src/requirements.txt

COPY . /src
WORKDIR /src

EXPOSE 8000

ENTRYPOINT chmod +x ./docker/wait && ./docker/wait && bash ./docker/entrypoint.sh