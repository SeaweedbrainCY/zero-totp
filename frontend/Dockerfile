FROM node:24-slim AS builder

RUN npm install -g @angular/cli --ignore-scripts


WORKDIR /app
COPY package.json package-lock.json ./


RUN npm ci --ignore-scripts


COPY . .

RUN ng build --configuration production --subresource-integrity
RUN chmod o+x ./generate_nginx_conf.sh
RUN chmod +x ./docker-healthcheck.sh
RUN ./generate_nginx_conf.sh
RUN rm generate_nginx_conf.sh


EXPOSE 80
FROM nginx:alpine
COPY --from=builder /app/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html/
COPY --from=builder /app/docker-healthcheck.sh /docker-healthcheck.sh
COPY --from=builder /app/entrypoint.sh /entrypoint.sh

# Temporary fix for CVE-2025-59375
RUN apk update --no-cache
RUN apk upgrade --no-cache

RUN chmod +x /docker-healthcheck.sh
RUN chmod +x /entrypoint.sh
RUN apk add --no-cache su-exec
ENTRYPOINT [ "/entrypoint.sh" ]
HEALTHCHECK --interval=1m --timeout=30s --start-period=10s --retries=2 CMD /docker-healthcheck.sh || exit 1