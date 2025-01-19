#!/bin/bash

cd
apt update 
sudo apt install git
apt install python3.11-venv
mkdir -p xl/templates/
cd xl
wget -q https://raw.githubusercontent.com/Sandhj/project/main/app2.py

cd templates
wget -q https://raw.githubusercontent.com/Sandhj/project/main/templates/dashboard_xl.html
wget -q https://raw.githubusercontent.com/Sandhj/project/main/templates/adminadduser.html

cd
cd xl
python3 -m venv web
source web/bin/activate

pip install flask
pip install requests
deactivate

cd
rm setup.sh
