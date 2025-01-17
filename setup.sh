#!/bin/bash

cd
apt update 
sudo apt install git

git clone https://github.com/Sandhj/project.git

cd project
python3 -m venv web
source web/bin/activate

pip install flask
pip isntall requests
deactivate

cd
cat <<EOL > /etc/systemd/system/app.service
[Unit]
Description=Flask App
After=network.target

[Service]
User=root
WorkingDirectory=/root/project
ExecStart=/root/project/venv/bin/python /root/project/app.py
Restart=always
Environment="PATH=/root/project/venv/bin"
Environment="VIRTUAL_ENV=/root/project/venv"
Environment="FLASK_APP=/root/project/app.py"

[Install]
WantedBy=multi-user.target

EOL

# Reload systemd dan aktifkan service
echo "Reloading systemd dan mengaktifkan service..."
systemctl daemon-reload
systemctl enable app.service

# Menjalankan service
systemctl start app.service

echo "Setup selesai. Service app.service telah berjalan."
