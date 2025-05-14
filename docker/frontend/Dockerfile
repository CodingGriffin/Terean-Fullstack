# syntax=docker.io/docker/dockerfile:1.7-labs
FROM node:18

EXPOSE 3000

WORKDIR /app

RUN npm i -g serve

COPY "frontend/package.json" "frontend/package-lock.json" ./

RUN npm ci

COPY --exclude="node_modules" --exclude="dist" frontend .

RUN npm run build

CMD [ "serve", "-s", "dist" ]
