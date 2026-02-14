#!/bin/bash

# Define variables
SERVICE_NAME="pi-server.service"
SOURCE_PATH=$(pwd)/$SERVICE_NAME
DEST_PATH="/etc/systemd/system/$SERVICE_NAME"

echo "--- Starting Systemd Setup ---"

# 1. Check if service file exists in current dir
if [ ! -f "$SOURCE_PATH" ]; then
    echo "Error: $SERVICE_NAME not found in current directory."
    exit 1
fi

# 2. Copy the service file to systemd directory
echo "Step 1: Copying service file to $DEST_PATH..."
sudo cp "$SOURCE_PATH" "$DEST_PATH"

# 3. Set correct ownership and permissions for the project folder
echo "Step 2: Tightening file permissions for security..."
sudo chown -R x1:www-data /home/x1/server
sudo chmod -R 750 /home/x1/server

# 4. Reload, Start, and Enable
echo "Step 3: Activating service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

# 5. Verify status
echo "--- Setup Complete ---"
sudo systemctl status "$SERVICE_NAME" --no-pager
