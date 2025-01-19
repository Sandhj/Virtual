from flask import Flask, render_template, flash, jsonify
import json
import os
import subprocess

app = Flask(__name__)
app.secret_key = os.urandom(24)
packages = {}
# Path file backup
BACKUP_FILE = 'backup_packages.json'
PASSWORD_FILE = 'password.txt'
PASSWORD_EXPIRY_DAYS = 30

@app.route('/') 
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
