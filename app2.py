from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# In-memory database untuk menyimpan daftar paket
packages = {}

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

@app.route('/adminku', methods=['GET'])
def admin_panel():
    return render_template('adminadduser.html')

@app.route('/')
def home():
    return render_template('dashboard_xl.html')
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
