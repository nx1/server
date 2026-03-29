#!/bin/bash
#sudo systemctl restart pi-server
#sudo systemctl status pi-server

# Old hacky way
sudo pkill -9 gunicorn
sudo systemctl daemon-reload
sudo systemctl restart pi-server
sudo systemctl status pi-server
