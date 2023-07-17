FROM python:3.9-slim

COPY . /api
WORKDIR /api

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools gcc default-libmysqlclient-dev pkg-config
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080

RUN chmod +x ./start.sh
USER 65534:65534
CMD ["./start.sh"]
