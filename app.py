from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import json
import os
import subprocess
import requests
import urllib.parse
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)
packages = {}
# Path file backup
BACKUP_FILE = 'backup_packages.json'
PASSWORD_FILE = 'password.txt'
PASSWORD_EXPIRY_DAYS = 30

#Fungsi kirim Data ke Bot Tele
def send_telegram_notification(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")

# Fungsi untuk mengambil data result
def data_result(protocol, username, expired, output):
    return {
        'username': username,
        'expired': expired,
        'protocol': protocol,
        'output': output
    }

# ------------------Funsgi awal web------------------

# Fungsi untuk memeriksa dan membuat password.txt jika belum ada
def check_and_create_password_file():
    if not os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'w') as file:
            file.write("")  # Membuat file kosong jika belum ada
        print("password.txt dibuat.")

# Fungsi untuk membaca password dan tanggal dari file
def read_passwords():
    passwords = []
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(" ", 1)
                if len(parts) == 2:
                    password = parts[0]
                    try:
                        created_at = datetime.strptime(parts[1], "%Y-%m-%d")
                        passwords.append((password, created_at))
                    except ValueError:
                        pass  # Abaikan jika format tanggal salah
    return passwords

# Fungsi untuk menambahkan password baru ke file
def add_password(password):
    with open(PASSWORD_FILE, 'a') as file:
        file.write(f"{password} {datetime.now().strftime('%Y-%m-%d')}\n")

# Halaman utama untuk login
@app.route('/', methods=['GET', 'POST'])
def login():
    check_and_create_password_file()  # Pastikan file password.txt ada

    if request.method == 'POST':
        entered_password = request.form['password']
        passwords = read_passwords()

        if not passwords:
            flash('Password belum diatur. Harap hubungi administrator untuk pengaturan password.', 'error')
            return redirect(url_for('login'))

        # Cek apakah password valid dan masih berlaku
        valid_password = False
        for stored_password, created_at in passwords:
            if entered_password == stored_password:
                if datetime.now() <= created_at + timedelta(days=PASSWORD_EXPIRY_DAYS):
                    valid_password = True
                    break
                else:
                    flash('Password sudah kadaluarsa. Harap hubungi administrator.', 'error')
                    break

        if valid_password:
            flash('Login berhasil!', 'success')
            return render_template('dashboard.html')
        else:
            flash('Password salah!', 'error')

    return render_template('login.html')

# Halaman admin untuk menambahkan password baru
@app.route('/adminadduser', methods=['GET', 'POST'])
def adminadduser():
    check_and_create_password_file()  # Pastikan file password.txt ada

    if request.method == 'POST':
        new_password = request.form['new_password']
        add_password(new_password)
        flash('Password berhasil ditambahkan!', 'success')
        return redirect(url_for('login'))

    return render_template('adminadduser.html')

# -------------- Dashboard -----------------
@app.route('/dashboard', methods=['POST'])
def dashboard():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        return render_template('dashboard.html')
                
# ---------------Fungsi Create Account------------
@app.route('/create_temp', methods=['GET', 'POST'])
def create_account_temp():
    if request.method == 'GET':
        return render_template('dashboard.html')
    elif request.method == 'POST':
        return render_template('create.html')

@app.route('/create', methods=['POST'])
def create_account():
    if request.method == 'POST':
        # Ambil data dari form
        protocol = request.form['protocol']
        device = request.form['device']
        username = request.form['username']
        expired = request.form['expired']

        # Debugging: Log data yang diterima dari form
        print(f"Received data - Protocol: {protocol}, Device: {device} Username: {username}, Expired: {expired}")

    # Menjalankan skrip shell dengan input dari user
    try:
        # Debugging: Log sebelum menjalankan skrip shell
        print(f"Running script for protocol: {protocol} with username: {username} and expired: {expired}")

        # Menjalankan skrip shell dengan memberikan input interaktif (username dan expired)
        result = subprocess.run(
            [f"/usr/bin/create_{protocol}"],  # Skrip untuk protokol (vmess, vless, trojan)
            input=f"{username}\n{expired}\n",  # Memberikan input username dan expired
            text=True,
            capture_output=True,
            check=True
        )
        
        # Jika berhasil, outputnya akan ditangkap oleh result.stdout
        print(f"Script output: {result.stdout.strip()}")
        
        # Kirim notifikasi ke bot Telegram admin
        telegram_token = "7360190308:AAH79nXyUiU4TRscBtYRLg14WVNfi1q1T1M"
        chat_id = "576495165"
        message = f"""
        <b>New Account Created</b>
        <b>Protocol:</b> {protocol}
        <b>Device :</b> {device}
        <b>Username:</b> {username}
        <b>Expired:</b> {expired} days
        """
        send_telegram_notification(telegram_token, chat_id, message)
        
    except subprocess.CalledProcessError as e:
        # Tangkap kesalahan jika terjadi error pada eksekusi skrip shell
        print(f"Error: {e.stderr.strip()}")
        output = f"Error: {e.stderr.strip()}"
        return render_template(
            'result.html',
            username=username,
            device=device,
            expired=expired,
            protocol=protocol,
            output=output
        )

    # Membaca file output yang dihasilkan oleh skrip shell
    output_file = f"/root/project/{username}_output.txt"
    if os.path.exists(output_file):
        with open(output_file, 'r') as file:
            output = file.read()

        # Menghapus file output setelah dibaca
        os.remove(output_file)

    # Mengalihkan ke halaman result
    return redirect(url_for('result', username=username, device=device, expired=expired, protocol=protocol, output=output))


@app.route('/renew_temp', methods=['GET', 'POST'])
def renew_account_temp():
    if request.method == 'GET':
        return render_template('dashboard.html')
    elif request.method == 'POST':
        return render_template('renew.html')

@app.route('/renew', methods=['POST'])
def renew_account():
    if request.method == 'POST':
        # Ambil data dari form
        protocol = request.form['protocol']
        device = request.form['device']
        username = request.form['username']
        expired = request.form['expired']

        # Debugging: Log data yang diterima dari form
        print(f"Received data - Protocol: {protocol}, Device: {device} Username: {username}, Expired: {expired}")

    # Menjalankan skrip shell dengan input dari user
    try:
        # Debugging: Log sebelum menjalankan skrip shell
        print(f"Running script for protocol: {protocol} with username: {username} and expired: {expired}")

        # Menjalankan skrip shell dengan memberikan input interaktif (username dan expired)
        result = subprocess.run(
            [f"/usr/bin/renew_{protocol}"],  # Skrip untuk protokol (vmess, vless, trojan)
            input=f"{username}\n{expired}\n",  # Memberikan input username dan expired
            text=True,
            capture_output=True,
            check=True
        )
        
        # Jika berhasil, outputnya akan ditangkap oleh result.stdout
        print(f"Script output: {result.stdout.strip()}")
        
        # Kirim notifikasi ke bot Telegram admin
        telegram_token = "7360190308:AAH79nXyUiU4TRscBtYRLg14WVNfi1q1T1M"
        chat_id = "576495165"
        message = f"""
        <b>New Account Created</b>
        <b>Protocol:</b> {protocol}
        <b>Device :</b> {device}
        <b>Username:</b> {username}
        <b>Expired:</b> {expired} days
        """
        send_telegram_notification(telegram_token, chat_id, message)
        
    except subprocess.CalledProcessError as e:
        # Tangkap kesalahan jika terjadi error pada eksekusi skrip shell
        print(f"Error: {e.stderr.strip()}")
        output = f"Error: {e.stderr.strip()}"
        return render_template(
            'result.html',
            username=username,
            device=device,
            expired=expired,
            protocol=protocol,
            output=output
        )

    # Membaca file output yang dihasilkan oleh skrip shell
    output_file = f"/root/project/{username}_output.txt"
    if os.path.exists(output_file):
        with open(output_file, 'r') as file:
            output = file.read()

        # Menghapus file output setelah dibaca
        os.remove(output_file)

    # Mengalihkan ke halaman result
    return redirect(url_for('result', username=username, device=device, expired=expired, protocol=protocol, output=output))
    
@app.route('/result')
def result():
    # Ambil data yang diterima dari URL dan tampilkan di result.html
    device = request.args.get('device')
    username = request.args.get('username')
    expired = request.args.get('expired')
    protocol = request.args.get('protocol')
    output = request.args.get('output')

    # Pastikan device memiliki nilai yang valid
    if device is None:
        device = "unknown"  # Nilai default jika device tidak ada

    # Tentukan harga berdasarkan device
    if device.lower() == "hp":
        price = "5.000"
    elif device.lower() == "stb":
        price = "10.000"
    else:
        price = "0"

    # Debugging: Log harga yang ditentukan
    print(f"Device: {device}, Price: {price}")

    # Pesan untuk WhatsApp
    wa_message = f"Selesaikan Pembayaran:\nProtokol: {protocol}\nUsername: {username}\nExpired: {expired}\nSebesar: {price}"

    # Encode pesan untuk URL WhatsApp
    wa_encoded_message = urllib.parse.quote(wa_message)
    wa_link = f"https://wa.me/6285155208019?text={wa_encoded_message}"  # Ganti <admin_number> dengan nomor admin

    return render_template(
        'result.html',
        username=username,
        expired=expired,
        protocol=protocol,
        device=device,
        output=output,
        wa_link=wa_link,
        price=price
    )

# ---------- Fungsi Kuota XL ----------
@app.route('/dashboard_xl', methods=['POST'])
def xl():
    return render_template('dashboard_xl.html')

@app.route('/adminku', methods=['GET'])
def admin():
    return render_template('adminku.html')

@app.route('/get_packages', methods=['GET'])
def get_packages():
    return jsonify(packages), 200

@app.route('/add_package', methods=['POST'])
def add_package():
    data = request.json
    name = data.get('name')
    detail = data.get('detail')

    if not name or not detail:
        return jsonify({'error': 'Nama dan detail paket wajib diisi!'}), 400

    if name in packages:
        return jsonify({'error': 'Paket dengan nama ini sudah ada!'}), 400

    packages[name] = detail
    return jsonify({'message': 'Paket berhasil ditambahkan!'}), 201

@app.route('/update_package/<string:package_name>', methods=['PUT'])
def update_package(package_name):
    data = request.json
    new_name = data.get('name')
    new_detail = data.get('detail')

    if not new_name or not new_detail:
        return jsonify({'error': 'Nama dan detail paket wajib diisi!'}), 400

    if package_name not in packages:
        return jsonify({'error': 'Paket tidak ditemukan!'}), 404

    # Perbarui paket dengan nama baru dan detail baru
    del packages[package_name]
    packages[new_name] = new_detail
    return jsonify({'message': 'Paket berhasil diperbarui!'}), 200

@app.route('/delete_package/<string:package_name>', methods=['DELETE'])
def delete_package(package_name):
    if package_name not in packages:
        return jsonify({'error': 'Paket tidak ditemukan!'}), 404

    del packages[package_name]
    return jsonify({'message': 'Paket berhasil dihapus!'}), 200

@app.route('/backup', methods=['POST'])
def backup_packages():
    try:
        # Simpan data packages ke file JSON
        with open(BACKUP_FILE, 'w') as file:
            json.dump(packages, file, indent=4)
        return jsonify({'message': 'Backup berhasil disimpan ke backup_packages.json'}), 200
    except Exception as e:
        return jsonify({'error': f'Gagal melakukan backup: {str(e)}'}), 500

@app.route('/restore', methods=['POST'])
def restore_packages():
    try:
        # Baca data dari file backup dan kembalikan ke memory
        global packages
        with open(BACKUP_FILE, 'r') as file:
            packages = json.load(file)
        return jsonify({'message': 'Data berhasil dipulihkan dari backup.'}), 200
    except FileNotFoundError:
        return jsonify({'error': 'File backup tidak ditemukan.'}), 404
    except Exception as e:
        return jsonify({'error': f'Gagal memulihkan data: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
