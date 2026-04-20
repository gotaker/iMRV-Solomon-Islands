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

# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim-bookworm AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH=/home/frappe/.local/bin:$PATH

# System deps. wkhtmltopdf is used by Frappe's PDF rendering.
# libmariadb-dev + mariadb-client needed for the mysqlclient Python driver.
# nginx + supervisor are the process orchestration layer.
# gosu lets entrypoint.sh drop from root to frappe user for bench commands.
# gettext-base provides envsubst, used to render nginx.conf with Railway's $PORT at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      curl \
      gettext-base \
      git \
      gosu \
      libmariadb-dev \
      libssl-dev \
      mariadb-client \
      nginx \
      pkg-config \
      redis-tools \
      supervisor \
      wkhtmltopdf \
      xfonts-75dpi \
      xfonts-base \
   && rm -rf /var/lib/apt/lists/*

# Node 20 for socketio + yarn
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && npm install -g yarn \
 && rm -rf /var/lib/apt/lists/*

# Create frappe user (uid 1000 to align with most Linux hosts for volume perms)
RUN groupadd -g 1000 frappe \
 && useradd -m -u 1000 -g 1000 -s /bin/bash frappe

# frappe-bench CLI, installed for the frappe user
USER frappe
WORKDIR /home/frappe
RUN pip install --user --no-cache-dir "frappe-bench==5.22.6" "click<8.1"
USER root

# ---------- bench init ----------
# Creates /home/frappe/frappe-bench with frappe framework checked out.
# --skip-assets: we build assets explicitly later (needs apps installed first).
# --skip-redis-config-generation: we point at Railway-managed Redis via
# common_site_config.json at runtime, not the local redis configs bench
# generates by default.
USER frappe
WORKDIR /home/frappe
RUN bench init \
      --python python3.11 \
      --frappe-branch version-15 \
      --skip-assets \
      --skip-redis-config-generation \
      --no-backups \
      frappe-bench

WORKDIR /home/frappe/frappe-bench
