FROM node:21-alpine

WORKDIR /app
ADD ./* ./
RUN npm install
RUN npm run build
