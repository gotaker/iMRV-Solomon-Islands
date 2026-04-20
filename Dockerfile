# syntax=docker/dockerfile:1.7

# ---------- Stage 1: Build Vue SPA ----------
FROM node:20-alpine AS frontend-build

# Mirror the bench directory layout so vite.config.js's dynamic outDir resolves
# correctly:  outDir = `../${basename(resolve('..'))}/public/frontend`
# With CWD at /build/mrvtools/frontend/, resolve('..') = /build/mrvtools and
# basename = 'mrvtools', so outDir becomes ../mrvtools/public/frontend which
# resolves to /build/mrvtools/mrvtools/public/frontend — matching the COPY targets.
WORKDIR /build/mrvtools

# Copy only what Vite needs (avoids invalidating cache on unrelated changes)
COPY frontend/package.json frontend/yarn.lock ./frontend/
RUN cd frontend && yarn install --frozen-lockfile

COPY frontend ./frontend
COPY mrvtools/public ./mrvtools/public
COPY mrvtools/www ./mrvtools/www

# The frontend package.json `build` script does:
#   vite build --base=/assets/mrvtools/frontend/ && yarn copy-html-entry
# which writes into ../mrvtools/public/frontend/ and ../mrvtools/www/frontend.html
RUN cd frontend && yarn build

# Sanity — fail the build if expected artifacts are missing
RUN test -d /build/mrvtools/mrvtools/public/frontend \
 && test -f /build/mrvtools/mrvtools/www/frontend.html
