FROM python:3.11-slim

# Install OpenSSH Server and Netcat
RUN apt-get update && apt-get install -y \
    openssh-server \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Setup SSH Directory
RUN mkdir -p /var/run/sshd

# Create user
RUN useradd -m -s /bin/bash starwars && \
    passwd -d starwars

# Copy App
WORKDIR /app
COPY . /app

# SSHD will refuse to start if the config is writable by others
RUN chmod +x /app/entrypoint.sh && \
    chmod 600 /app/sshd_config && \
    chown root:root /app/sshd_config

EXPOSE 2222 2323

CMD ["/app/entrypoint.sh"]
