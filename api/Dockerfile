FROM python:3.13.15-alpine3.24 AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv

# Install into /api/venv (admin-toolbox.sh relies on this path) using the image's Python only
ENV UV_PROJECT_ENVIRONMENT=/api/venv
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_LINK_MODE=copy

WORKDIR /api

RUN apk update && apk upgrade && apk add --no-cache mariadb-dev  gcc g++ libffi-dev openssl-dev musl-dev linux-headers make jq curl gosu && apk add --no-cache mariadb-connector-c-dev

COPY pyproject.toml uv.lock /api/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


FROM python:3.13.15-alpine3.24

COPY --from=builder /api/venv /api/venv
# Remove pip to remove pip pre-imported packages (the uv venv doesn't ship pip)
RUN python -m pip uninstall -y pip \
&& rm -rf /usr/local/lib/python3.13/ensurepip


ENV PATH="/api/venv/bin:$PATH"

RUN apk update && apk upgrade && apk add --no-cache jq curl gosu mariadb-connector-c-dev libgcc libstdc++

WORKDIR /api

COPY assets/ /api/assets/
COPY CryptoClasses/ /api/CryptoClasses/
COPY database/ /api/database/
COPY Email/ /api/Email/
COPY endpoints_controllers/ /api/endpoints_controllers/
COPY migrations/ /api/migrations/
COPY monitoring/ /api/monitoring/
COPY Services/ /api/Services/
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
