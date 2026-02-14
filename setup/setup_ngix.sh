sudo apt update
sudo apt install nginx
sudo cp homeserver /etc/nginx/sites-available/homeserver
sudo nginx -t && sudo systemctl reload nginx
