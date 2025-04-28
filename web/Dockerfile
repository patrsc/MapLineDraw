FROM node:22.15

WORKDIR /app

COPY package.json .
COPY package-lock.json .

RUN npm ci

COPY assets assets
COPY components components
COPY plugins plugins
COPY public public
COPY server server
COPY types types
COPY utils utils
COPY app.vue .
COPY nuxt.config.ts .
COPY tsconfig.json .

RUN npm run build

ENTRYPOINT [ "node", ".output/server/index.mjs" ]
