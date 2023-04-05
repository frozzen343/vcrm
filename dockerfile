FROM python:3.9

COPY ./requirements.txt /src/requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /src/requirements.txt

COPY . /src
WORKDIR /src

EXPOSE 8000

RUN chmod +x ./docker/entrypoint.sh
RUN chmod +x ./docker/wait
ENTRYPOINT ./docker/wait && bash ./docker/entrypoint.sh