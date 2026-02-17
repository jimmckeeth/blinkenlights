#!/bin/bash

# Start Python Server for TELNET (Port 2323)
python3 starwars-server.py --port 2323 
# Removed & so it runs in FOREGROUND

# Start Python Server for SSH (Port 2324 - RAW mode)
# python3 starwars-server.py --port 2324 --raw &

# Generate SSH Host Keys
# ssh-keygen -A

# Start SSH Daemon
# -D: Do not detach (foreground)
# -e: Log to stderr (so we see errors in docker logs)
# -f: Custom config path
# echo "Starting SSHD..."
# exec /usr/sbin/sshd -D -e -f /app/sshd_config
