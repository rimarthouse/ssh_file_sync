ARG BUILD_FROM=ghcr.io/hassio-addons/base:12.2.0
FROM $BUILD_FROM

# Set shell options
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Python and dependencies
RUN apk add --no-cache python3 py3-pip && \
    pip3 install paramiko pyyaml

# Copy addon files
COPY run.sh /run.sh
COPY sync.py /sync.py

# Set permissions
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]