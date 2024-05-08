# build env
FROM node:13.12.0-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
# RUN npm install --force
COPY . ./
RUN npm run build
# RUN cp -r build result_build
# CMD cp -r build result_build
# RUN npm install --global http-server
# CMD ["npx", "-y", "http-server", "-p", "8000", "/app/build"]