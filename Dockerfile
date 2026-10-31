# syntax=docker/dockerfile:1
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=secret,id=ca_bundle,required=true \
    apt-get -o Acquire::https::CaInfo=/run/secrets/ca_bundle update && \
    apt-get -o Acquire::https::CaInfo=/run/secrets/ca_bundle install -y --no-install-recommends bash ca-certificates curl git python3 sudo procps util-linux kmod && \
    rm -rf /var/lib/apt/lists/*
COPY vendor/install.sh /tmp/gentle-ai-install.sh
RUN --mount=type=secret,id=ca_bundle,required=true \
    CURL_CA_BUNDLE=/run/secrets/ca_bundle SSL_CERT_FILE=/run/secrets/ca_bundle \
    bash /tmp/gentle-ai-install.sh --method binary --dir /usr/local/bin && \
    rm /tmp/gentle-ai-install.sh
RUN useradd -m -s /bin/bash developer && mkdir -p /project && chown developer:developer /project
USER developer
WORKDIR /project
CMD ["sleep", "infinity"]
