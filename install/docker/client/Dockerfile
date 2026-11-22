FROM kalilinux/kali-rolling AS build

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      git \
      nodejs \
      npm \
      python3 \
      make \
      g++ \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/nukerat/client/gui
COPY client/gui/package.json client/gui/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY client/gui/ ./
RUN npx electron-vite build \
 && npx electron-builder --linux dir \
 && test -x dist/linux-unpacked/nukerat

FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ELECTRON_OZONE_PLATFORM_HINT=auto

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      python3 \
      libgtk-3-0t64 \
      libnss3 \
      libnspr4 \
      libxss1 \
      libxtst6 \
      libx11-xcb1 \
      libxcb-dri3-0 \
      libdrm2 \
      libgbm1 \
      libasound2t64 \
      libxkbcommon0 \
      libxcomposite1 \
      libxdamage1 \
      libxfixes3 \
      libxrandr2 \
      libcups2t64 \
      libatk-bridge2.0-0t64 \
      libatk1.0-0t64 \
      libatspi2.0-0t64 \
      libsecret-1-0 \
      fonts-liberation \
      xdg-utils \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/nukerat
COPY nukerat.py LICENSE DISCLAIMER.md /opt/nukerat/
COPY --from=build /opt/nukerat/client/gui/dist/linux-unpacked /opt/nukerat/client/gui/dist/linux-unpacked

RUN printf '%s\n' \
      '#!/bin/sh' \
      'exec /opt/nukerat/client/gui/dist/linux-unpacked/nukerat --no-sandbox "$@"' \
      > /usr/local/bin/nukerat-gui \
 && printf '%s\n' '#!/bin/sh' 'exec python3 /opt/nukerat/nukerat.py "$@"' > /usr/local/bin/nukerat \
 && chmod 0755 /usr/local/bin/nukerat-gui /usr/local/bin/nukerat \
 && useradd --create-home --uid 1000 --shell /bin/bash nukerat \
 && chown -R nukerat:nukerat /opt/nukerat

USER nukerat
WORKDIR /opt/nukerat

ENTRYPOINT ["nukerat"]
CMD ["client", "start"]
