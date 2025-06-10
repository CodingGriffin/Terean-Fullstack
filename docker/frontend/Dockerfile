# syntax=docker.io/docker/dockerfile:1.7-labs
FROM node:18

RUN apt update && apt install nginx vim -y

WORKDIR /app

COPY "frontend/package.json" "frontend/package-lock.json" ./

RUN npm ci

COPY --exclude="node_modules" --exclude="dist" frontend .

RUN npm run build

RUN rm /var/www/html/index.nginx-debian.html && mv dist/* /var/www/html

COPY nginx/ ./nginx

COPY data/ ./data

RUN rm /etc/nginx/sites-enabled/default && mv /app/data/sites-enabled/* /etc/nginx/sites-enabled/ 

CMD ["nginx", "-g", "daemon off;"]
