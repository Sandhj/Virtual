# Path absolut ke virtual environment
VENV_PATH="/root/project/web"
# Path absolut ke aplikasi
APP_PATH="/root/project/app.py"
# Menjalankan aplikasi menggunakan Python dari virtual environment dan mengalihkan output
$VENV_PATH/bin/python $APP_PATH > /root/project/app.log 2>&1 &
