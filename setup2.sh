#!/bin/bash

cd
apt update 
sudo apt install git
mkdir -p xl/templates/
cd xl
wget -q https://raw.githubusercontent.com/Sandhj/project/main/app2.sh

cd templates
wget -q https://raw.githubusercontent.com/Sandhj/project/main/dashboard_xl.sh
wget -q https://raw.githubusercontent.com/Sandhj/project/main/adminadduser.sh

cd
cd xl
python3 -m venv web
source web/bin/activate

pip install flask
pip install requests
deactivate

cd
rm setup.sh
