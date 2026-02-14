# Firewall
sudo apt install ufw
sudo ufw allow in on tailscale0
sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp
sudo ufw deny in on wlan0
