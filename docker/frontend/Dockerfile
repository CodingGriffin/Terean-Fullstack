# syntax=docker.io/docker/dockerfile:1.7-labs
FROM node:18

WORKDIR /app

COPY "frontend/package.json" .

RUN npm install

RUN npm i -g serve

COPY --exclude="frontend/node_modules" frontend .

RUN npm run build

EXPOSE 3000

CMD [ "serve", "-s", "dist" ]
