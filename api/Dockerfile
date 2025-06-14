FROM python:3.12-slim

COPY . /api
WORKDIR /api

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools gcc default-libmysqlclient-dev pkg-config jq curl gosu
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080

RUN chmod +x ./start.sh
RUN chmod +x ./docker-healthcheck.sh
RUN chmod +x ./entrypoint.sh
RUN mkdir /api/logs
CMD ["./entrypoint.sh"]
HEALTHCHECK --interval=1m --timeout=30s --start-period=10s --retries=2 CMD ./docker-healthcheck.sh || exit 1