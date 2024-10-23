FROM node:20-slim AS builder

RUN npm install -g @angular/cli --ignore-scripts


WORKDIR /app
COPY package.json package-lock.json ./


RUN npm ci --ignore-scripts


COPY . .

RUN ng build --configuration production --subresource-integrity
RUN chmod o+x ./generate_CSP_hashes.sh
RUN ./generate_CSP_hashes.sh
RUN rm generate_CSP_hashes.sh


EXPOSE 80
FROM nginx:alpine
RUN  touch /var/run/nginx.pid && \
     chown -R nginx:nginx /var/cache/nginx /var/run/nginx.pid
USER nginx
COPY --from=builder /app/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html/

