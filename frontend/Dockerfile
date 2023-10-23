FROM node:20-slim AS builder

RUN npm install -g @angular/cli


WORKDIR /app
COPY package.json package-lock.json ./


RUN npm ci


COPY . .

RUN ng build --configuration production

EXPOSE 80
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html/

