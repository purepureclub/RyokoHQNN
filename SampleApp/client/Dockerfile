FROM node:alpine as build
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY package.json /usr/src/app
COPY package-lock.json /usr/src/app
RUN npm install
COPY . /usr/src/app
RUN npm run build

FROM nginxinc/nginx-unprivileged
COPY --from=build /usr/src/app/build /usr/share/nginx/html