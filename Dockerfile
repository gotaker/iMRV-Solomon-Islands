# syntax=docker/dockerfile:1.7

# ---------- Stage 1: Build Vue SPA ----------
FROM node:24-alpine AS frontend-build

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
FROM python:3.14-slim-bookworm AS runtime

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
      file \
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

# Node 24 for socketio + yarn
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && npm install -g yarn \
 && rm -rf /var/lib/apt/lists/*

# Create frappe user (uid 1000 to align with most Linux hosts for volume perms)
RUN groupadd -g 1000 frappe \
 && useradd -m -u 1000 -g 1000 -s /bin/bash frappe

# frappe-bench CLI, installed for the frappe user
USER frappe
WORKDIR /home/frappe
RUN pip install --user --no-cache-dir frappe-bench
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
      --python python3.14 \
      --frappe-branch version-16 \
      --skip-assets \
      --skip-redis-config-generation \
      --no-backups \
      frappe-bench

WORKDIR /home/frappe/frappe-bench

# ---------- Stage apps into the build context ----------
USER root

# Copy the whole repo into /src, owned by frappe. .dockerignore excludes .git,
# so bench get-app (which calls git.Repo(src)) would fail on the bare tree —
# we init a throwaway git repo in /src with a single commit.
RUN mkdir -p /src && chown frappe:frappe /src
COPY --chown=frappe:frappe . /src

USER frappe
WORKDIR /src
RUN git -c init.defaultBranch=master init -q \
 && git -c user.name=docker -c user.email=docker@local add -A \
 && git -c user.name=docker -c user.email=docker@local commit -q -m "docker build snapshot"

WORKDIR /home/frappe/frappe-bench

# --- Stage mrvtools ---
# The repo root IS the mrvtools Python package (setup.py at /src/setup.py
# installs the mrvtools module at /src/mrvtools).
RUN bench get-app --skip-assets mrvtools /src

# --- Stage frappe_side_menu ---
# frappe_side_menu's module lives at /src/frappe_side_menu/ but its setup file
# is /src/setup_sidebarmenu.py. bench get-app can't handle that shape, so we
# stage it into .stage/frappe_side_menu/ with setup.py copied in + git-init'd.
RUN set -eux; \
    STAGE=/home/frappe/frappe-bench/.stage/frappe_side_menu; \
    rm -rf "$STAGE"; \
    mkdir -p "$STAGE"; \
    cp -R /src/frappe_side_menu "$STAGE/frappe_side_menu"; \
    cp /src/setup_sidebarmenu.py "$STAGE/setup.py"; \
    cp /src/requirements.txt "$STAGE/requirements.txt"; \
    if [ -f /src/license.txt ]; then cp /src/license.txt "$STAGE/license.txt"; fi; \
    cd "$STAGE"; \
    git -c init.defaultBranch=master init -q; \
    git -c user.name=docker -c user.email=docker@local add -A; \
    git -c user.name=docker -c user.email=docker@local commit -q -m stage; \
    cd /home/frappe/frappe-bench; \
    bench get-app --skip-assets frappe_side_menu "$STAGE"

# ---------- Inject pre-built SPA from stage 1 ----------
# The SPA was already built in the frontend-build stage. Copy it into the
# mrvtools app inside the bench so /assets/mrvtools/frontend/ resolves.
# Note: stage 1's WORKDIR is /build/mrvtools; vite.config.js resolves outDir
# using basename(cwd-parent), so the artifacts end up at
# /build/mrvtools/mrvtools/public/frontend and /build/mrvtools/mrvtools/www/frontend.html.
COPY --from=frontend-build --chown=frappe:frappe \
    /build/mrvtools/mrvtools/public/frontend \
    /home/frappe/frappe-bench/apps/mrvtools/mrvtools/public/frontend

COPY --from=frontend-build --chown=frappe:frappe \
    /build/mrvtools/mrvtools/www/frontend.html \
    /home/frappe/frappe-bench/apps/mrvtools/mrvtools/www/frontend.html

# ---------- bench build ----------
# Bundles Frappe's own JS/CSS + mrvtools + frappe_side_menu into
# sites/assets/. Required for the Frappe desk to load.
#
# The root package.json for mrvtools has a `build` script that runs
# `cd frontend && yarn build`. Frappe's esbuild pipeline passes
# --run-build-command which triggers that script — but frontend/node_modules
# does not exist in the bench (Vite is only in stage 1). Since the SPA is
# already pre-built and copied above, we stub that script out with a no-op
# before invoking bench build.
RUN node -e " \
    const fs = require('fs'); \
    const p = '/home/frappe/frappe-bench/apps/mrvtools/package.json'; \
    const pkg = JSON.parse(fs.readFileSync(p, 'utf8')); \
    if (pkg.scripts && pkg.scripts.build) { \
        pkg.scripts.build = 'echo SPA already built in stage 1, skipping'; \
    } \
    fs.writeFileSync(p, JSON.stringify(pkg, null, 2)); \
"

RUN cd /home/frappe/frappe-bench \
 && bench build --apps frappe,mrvtools,frappe_side_menu

# ---------- Optional: bake in a sample DB dump ----------
# Entrypoint.sh auto-uses /home/frappe/sample-db/*.sql.gz when present and
# SAMPLE_DB_URL / SAMPLE_DB_PATH aren't set. `.Sample DB/` is gitignored by
# default (see .gitignore — only .gitkeep is tracked), so Railway's git
# checkout gives an empty dir and the COPY is a no-op. To bake a dump in:
# either commit a *.sql.gz into .Sample DB/ (temporarily un-ignore it), or
# `docker build` locally with the dump present in the build context.
USER root
RUN mkdir -p /home/frappe/sample-db && chown -R frappe:frappe /home/frappe/sample-db
COPY --chown=frappe:frappe [".Sample DB", "/home/frappe/sample-db/"]
USER frappe

# ---------- Snapshot the sites/ skeleton ----------
# If the runtime mounts a persistent volume at /home/frappe/frappe-bench/sites,
# the mount shadows the apps.txt, assets/, and other files bench init/build
# wrote into sites/. The entrypoint seeds an empty volume from this snapshot.
RUN cp -a /home/frappe/frappe-bench/sites /home/frappe/sites-template \
 && chown -R frappe:frappe /home/frappe/sites-template

# ---------- Configs + entrypoint ----------
USER root

COPY deploy/railway/supervisord.conf /etc/supervisor/supervisord.conf
COPY deploy/railway/nginx.conf.template /etc/nginx/nginx.conf.template
COPY deploy/railway/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Pre-create log + run dirs for supervisor/nginx
RUN mkdir -p /var/log/supervisor /var/run \
 && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf 2>/dev/null || true

# Railway injects $PORT. We expose a conventional value for documentation;
# actual listen port is set by envsubst at entrypoint time.
EXPOSE 8080

WORKDIR /home/frappe/frappe-bench

ENTRYPOINT ["/entrypoint.sh"]
