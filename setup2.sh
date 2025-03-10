#!/bin/bash

cd
apt update 
sudo apt install git
apt install python3.11-venv
mkdir -p xl/templates/
cd xl
wget -q https://raw.githubusercontent.com/Sandhj/project/main/app2.py

cat <<EOL > run.sh
#!/bin/bash
source /root/xl/web/bin/activate
python /root/xl/app2.py
EOL

cd templates
wget -q https://raw.githubusercontent.com/Sandhj/project/main/templates/dashboard_xl.html
wget -q https://raw.githubusercontent.com/Sandhj/project/main/templates/adminku.html

cd
cd xl
python3 -m venv web
source web/bin/activate

pip install flask
pip install requests
deactivate

cd
rm setup.sh
