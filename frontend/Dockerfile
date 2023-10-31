FROM node:20-slim AS builder

RUN npm install -g @angular/cli


WORKDIR /app
COPY package.json package-lock.json ./


RUN npm ci


COPY . .

RUN ng build --configuration production --subresource-integrity

EXPOSE 80
FROM nginx:alpine
RUN  touch /var/run/nginx.pid && \
     chown -R nginx:nginx /var/cache/nginx /var/run/nginx.pid
USER nginx
COPY  nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html/

