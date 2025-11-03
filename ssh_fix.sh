#!/bin/bash

# SSH Configuration Fix for Raspberry Pi Zero 2
# Standalone script to fix common SSH issues
# Run with: bash ssh_fix.sh

echo "=== SSH Fix for Raspberry Pi Zero 2 ==="
echo

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    echo "Some features may not work correctly."
    echo
fi

# Enable SSH service
echo "1. Enabling SSH service..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Create SSH directory if it doesn't exist
echo "2. Setting up SSH directory..."
if [ ! -d "/home/$USER/.ssh" ]; then
    mkdir -p /home/$USER/.ssh
    chmod 700 /home/$USER/.ssh
    chown $USER:$USER /home/$USER/.ssh
    echo "   ✓ Created ~/.ssh directory"
else
    echo "   ✓ ~/.ssh directory already exists"
fi

# Backup existing SSH config if it exists
if [ -f "/etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf" ]; then
    echo "3. Backing up existing SSH configuration..."
    sudo cp /etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf /etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf.backup
fi

# Apply SSH configuration fixes
echo "3. Applying SSH configuration fixes..."
sudo tee /etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf > /dev/null << 'EOF'
# SSH Configuration fixes for Raspberry Pi Zero 2
# Improve connection stability and compatibility

# Allow password authentication (can be disabled later for security)
PasswordAuthentication yes
PubkeyAuthentication yes

# Increase connection limits
MaxAuthTries 6
MaxSessions 10

# Optimize for slower hardware
LoginGraceTime 120
ClientAliveInterval 60
ClientAliveCountMax 3

# Enable compression to help with slower connections
Compression yes

# Allow root login with key only (more secure)
PermitRootLogin prohibit-password

# Disable DNS lookups to speed up connections
UseDNS no

# Set proper ciphers for Pi Zero 2 performance
Ciphers aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-256,hmac-sha2-512,hmac-sha1

# Keep connections alive
TCPKeepAlive yes
EOF

# Test SSH configuration
echo "4. Testing SSH configuration..."
if sudo sshd -t; then
    echo "   ✓ SSH configuration is valid"
else
    echo "   ⚠ SSH configuration has errors - restoring backup if available"
    if [ -f "/etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf.backup" ]; then
        sudo mv /etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf.backup /etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf
    else
        sudo rm -f /etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf
    fi
    echo "   Please check SSH logs: sudo journalctl -u ssh"
    exit 1
fi

# Restart SSH service
echo "5. Restarting SSH service..."
sudo systemctl restart ssh

# Check if SSH is running
if sudo systemctl is-active --quiet ssh; then
    echo "   ✓ SSH service is running"
else
    echo "   ⚠ SSH service failed to start - check logs with: sudo journalctl -u ssh"
    exit 1
fi

# Display connection information
echo
echo "=== SSH Fix Complete! ==="
echo
echo "SSH Connection Information:"
echo "  Username: $USER"
echo "  Port: 22"
echo "  IP Address: $(hostname -I | awk '{print $1}')"
echo
echo "Connection command:"
echo "  ssh $USER@$(hostname -I | awk '{print $1}')"
echo
echo "Troubleshooting:"
echo "  - Check SSH status: sudo systemctl status ssh"
echo "  - View SSH logs: sudo journalctl -u ssh"
echo "  - Test connection: ssh -v $USER@localhost"
echo
echo "Security recommendations:"
echo "  1. Set up SSH keys for passwordless login"
echo "  2. Consider disabling password authentication after key setup"
echo "  3. Change default SSH port if needed"
echo
