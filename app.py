from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import json
import os
import subprocess
import requests
import urllib.parse

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
@app.route('/')
def login():
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
