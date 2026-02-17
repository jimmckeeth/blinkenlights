#!/bin/bash

# 1. Generate SSH Host Keys
ssh-keygen -A

# 2. Start Python Server for TELNET (Port 2323)
python3 starwars-server.py --port 2323 &

# 3. Start Python Server for SSH (Port 2324 - RAW mode)
python3 starwars-server.py --port 2324 --raw &

# 4. Start SSH Daemon
# -D: Do not detach (foreground)
# -e: Log to stderr (so we see errors in docker logs)
# -f: Custom config path
echo "Starting SSHD..."
exec /usr/sbin/sshd -D -e -f /app/sshd_config