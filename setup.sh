#!/bin/bash

cd
apt update 
sudo apt install git

git clone

cd project
python3 -m venv web
source web/bin/activate

pip install flask
pip isntall requests
deactivate

cd
# Direktori proyek
PROJECT_DIR="/root/project"
VENV_DIR="$PROJECT_DIR/web"
APP_FILE="$PROJECT_DIR/app.py"
SERVICE_FILE="/etc/systemd/system/app.service"

# Periksa apakah direktori proyek ada
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Membuat direktori proyek di $PROJECT_DIR..."
    mkdir -p "$PROJECT_DIR"
fi

# Buat virtual environment jika belum ada
if [ ! -d "$VENV_DIR" ]; then
    echo "Membuat virtual environment di $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Aktifkan venv dan instal dependensi
echo "Menginstal dependensi di venv..."
source "$VENV_DIR/bin/activate"
pip install -r "$PROJECT_DIR/requirements.txt"

# Buat file systemd service
echo "Membuat file service di $SERVICE_FILE..."
cat <<EOL > $SERVICE_FILE
[Unit]
Description=Python Web Application Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python $APP_FILE
Restart=always
RestartSec=5
Environment="PATH=$VENV_DIR/bin"
Environment="VIRTUAL_ENV=$VENV_DIR"

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd dan aktifkan service
echo "Reloading systemd dan mengaktifkan service..."
systemctl daemon-reload
systemctl enable app.service

# Menjalankan service
echo "Menjalankan service..."
systemctl start app.service

echo "Setup selesai. Service app.service telah berjalan."
