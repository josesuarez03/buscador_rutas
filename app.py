from flask import Flask, render_template, request, jsonify
import subprocess
import pymongo
import requests
from threading import Thread
import connect

app = Flask(__name__)

app.static_folder = 'static'
app.secret_key = 'your_secret_key'

db = connect.connect_mongo()

DEFAULT_WORDLIST = "/usr/share/dirb/wordlists/common.txt"

def run_dirb(url, wordlist=DEFAULT_WORDLIST):
    try:
        output = subprocess.check_output(["/usr/local/bin/dirb", url, wordlist])
        return [line.split()[1] for line in output.decode().splitlines() if line.startswith("[+]")]
    except subprocess.CalledProcessError as e:
        print(f"Error al escanear {url}: {e}")
        return None

def save_discovered_routes(url):
    discovered_routes = run_dirb(url)
    if discovered_routes:
        routes_collection = db["routes"]
        data_collection = db["data"]
        for route in discovered_routes:
            routes_collection.insert_one({"url": url, "route": route})
            response = requests.get(route)
            data_collection.insert_one({"route": route, "status_code": response.status_code})
    return discovered_routes

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['query']
        thread = Thread(target=save_discovered_routes, args=(url,))
        thread.start()
        return f"Escaneo iniciado para: {url}. Verifique más tarde para los resultados."
    return render_template('index.html')

@app.route('/discover', methods=['POST'])
def discover():
    url = request.form['query']
    discovered_routes = save_discovered_routes(url)
    if discovered_routes:
        return jsonify({"message": "Rutas descubiertas y guardadas"})
    else:
        return jsonify({"error": "Error al descubrir rutas"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
