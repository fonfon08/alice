FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      xz-utils \
      libsnappy1v5 \
      libsnappy-dev \
      libcairo2 \
      libffi8 \
      libgdk-pixbuf-2.0-0 \
      libpango-1.0-0 \
      libpangocairo-1.0-0 \
      shared-mime-info \
      fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/nukerat
COPY install.sh /opt/nukerat/install.sh
COPY install/ /opt/nukerat/install/
COPY nukerat.py /opt/nukerat/nukerat.py
COPY LICENSE DISCLAIMER.md /opt/nukerat/
COPY server/ /opt/nukerat/server/
COPY implants/ /opt/nukerat/implants/

RUN bash install.sh server \
 && printf '%s\n' '#!/bin/sh' 'exec python3 /opt/nukerat/nukerat.py "$@"' > /usr/local/bin/nukerat \
 && chmod 0755 /usr/local/bin/nukerat \
 && useradd --create-home --uid 1000 --shell /bin/bash nukerat \
 && chown -R nukerat:nukerat /opt/nukerat \
 && rm -rf \
      /var/lib/apt/lists/* \
      /root/.cache \
      /root/.cargo/registry \
      /root/.cargo/git \
      /opt/nukerat/server/infra/bin/encoders/sgn/target

USER nukerat
WORKDIR /opt/nukerat

EXPOSE 9000

ENTRYPOINT ["nukerat"]
CMD ["server", "start"]
