#!/bin/bash

cd
apt update 
sudo apt install git

git clone https://github.com/Sandhj/project.git

cd project
python3 -m venv web
source web/bin/activate

pip install flask
pip install requests
deactivate

cd
cat <<EOL > /etc/systemd/system/app.service
[Unit]
Description=Run project script
After=network.target

[Service]
ExecStart=/bin/bash /root/project/run.sh
WorkingDirectory=/root/project
User=root
Group=root
Restart=always
StandardOutput=journal
StandardError=journal
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd dan aktifkan service
systemctl daemon-reload
systemctl enable app.service

# Menjalankan service
systemctl start app.service

echo "Setup selesai. Service app.service telah berjalan."

cd
rm setup.sh
