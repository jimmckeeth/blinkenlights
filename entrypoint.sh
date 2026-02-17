#!/bin/bash

# 1. Generate SSH Host Keys (required if they don't exist)
ssh-keygen -A

# 2. Start Python Server for TELNET (Port 2323 -> Mapped to 23 outside)
# This one sends Telnet headers.
python3 starwars-server.py --port 2323 &

# 3. Start Python Server for SSH (Port 2324 -> Internal only)
# This one is RAW (no headers) so SSH clients don't see garbage.
python3 starwars-server.py --port 2324 --raw &

# 4. Start SSH Daemon in foreground
echo "Starting SSHD..."
/usr/sbin/sshd -D -f /app/sshd_config