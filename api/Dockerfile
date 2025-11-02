FROM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /api/requirements.txt
WORKDIR /api
RUN python -m venv /api/venv
ENV PATH="/api/venv/bin:$PATH"

RUN apk update && apk upgrade && apk add --no-cache mariadb-dev  gcc g++ libffi-dev openssl-dev musl-dev linux-headers make jq curl gosu && apk add --no-cache mariadb-connector-c-dev 

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


FROM python:3.13-alpine

COPY --from=builder /api/venv /api/venv
ENV PATH="/api/venv/bin:$PATH"

RUN apk update && apk upgrade && apk add --no-cache jq curl gosu mariadb-connector-c-dev  gcc g++

WORKDIR /api

COPY assets/ /api/assets/
COPY CryptoClasses/ /api/CryptoClasses/
COPY database/ /api/database/
COPY Email/ /api/Email/
COPY endpoints_controllers/ /api/endpoints_controllers/
COPY migrations/ /api/migrations/
COPY monitoring/ /api/monitoring/
COPY Oauth/ /api/Oauth/
COPY openAPI/ /api/openAPI/
COPY toolbox_scripts/ /api/toolbox_scripts/
COPY Utils/ /api/Utils/
COPY admin-toolbox.sh /api/
COPY alembic.ini /api/
COPY app.py /api/
COPY controllers.py /api/
COPY docker-healthcheck.sh /api/
COPY entrypoint.sh /api/
COPY environment.py /api/
COPY start.sh /api/
COPY VERSION /api/

EXPOSE 8080

RUN chmod +x ./start.sh
RUN chmod +x ./docker-healthcheck.sh
RUN chmod +x ./entrypoint.sh
RUN mkdir /api/logs
CMD ["./entrypoint.sh"]
HEALTHCHECK --interval=1m --timeout=30s --start-period=10s --retries=2 CMD ./docker-healthcheck.sh || exit 1