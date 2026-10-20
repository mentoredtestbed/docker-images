#!/bin/bash
# Start sshd with weak credentials for vulnerability testing
# This script runs AT CONTAINER STARTUP — sshd is already installed in the image build.
# Used as the vulnerable target container (home-webserver).

set -e

# Initialize sshd (generate host keys if missing)
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    ssh-keygen -A
fi

# Set weak root password for brute-force testing
echo "root:toor" | chpasswd

# Enable root login with password authentication (required for brute-force testing)
sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
grep -q '^PermitRootLogin' /etc/ssh/sshd_config || echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

# Ensure password authentication is enabled
sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
grep -q '^PasswordAuthentication' /etc/ssh/sshd_config || echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Start rsyslog for sshd logging (rsyslog already installed in image)
if command -v rsyslogd &> /dev/null; then
    rsyslogd
fi

# Start sshd in foreground (required for container)
exec /usr/sbin/sshd -D