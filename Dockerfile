ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

# Install system requirements
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-setuptools \
    py3-wheel \
    sqlite \
    nodejs \
    npm

# Copy data
COPY run.sh /
COPY app/ /app/
COPY www/ /www/

# Create virtual environment and install ALL Python dependencies via pip
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir \
    flask \
    flask-socketio \
    pyyaml \
    schedule \
    requests \
    python-crontab

# Update PATH to use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Ensure static files are in place (they're already copied)
WORKDIR /www

# Make run script executable
RUN chmod a+x /run.sh

# Expose port
EXPOSE 8099

CMD [ "/run.sh" ]