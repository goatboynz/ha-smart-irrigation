ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-flask \
    py3-requests \
    py3-yaml \
    py3-schedule \
    nodejs \
    npm

# Copy data
COPY run.sh /
COPY app/ /app/
COPY www/ /www/

# Install Python dependencies
RUN pip3 install --no-cache-dir flask flask-socketio pyyaml schedule requests python-crontab

# Install Node.js dependencies and build frontend
WORKDIR /www
RUN npm install && npm run build

# Make run script executable
RUN chmod a+x /run.sh

# Expose port
EXPOSE 8099

CMD [ "/run.sh" ]