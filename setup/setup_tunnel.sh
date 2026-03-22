#!/bin/bash

# Define paths
CONFIG_SRC="/etc/cloudflared/config.yml"
SERVICE_FILE="/etc/systemd/system/cloudflared.service"

echo "--- Starting Cloudflare Tunnel Setup ---"

# 1. Ensure cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "Error: cloudflared not found. Please install it first."
    exit 1
fi

# 2. Install the service (if not already installed)
if [ ! -f "$SERVICE_FILE" ]; then
    echo "Step 1: Installing cloudflared system service..."
    sudo cloudflared service install
else
    echo "Step 1: Service already installed. Skipping."
fi

# 3. Add Nginx dependency (The "No Corners" reliability tweak)
# This ensures the tunnel waits for Nginx to be ready before starting
echo "Step 2: Adding Nginx dependency to service..."
sudo sed -i '/After=network.target/a After=nginx.service' "$SERVICE_FILE"
sudo sed -i '/After=nginx.service/a Requires=nginx.service' "$SERVICE_FILE"

# 4. Reload and Restart
echo "Step 3: Reloading and Restarting..."
sudo systemctl daemon-reload
sudo systemctl enable cloudflared
sudo systemctl restart cloudflared

echo "--- Setup Complete ---"
sudo systemctl status cloudflared --no-pager
