from flask import Flask, render_template, request, jsonify
import subprocess
import requests
from threading import Thread
import connect

app = Flask(__name__)

app.static_folder = 'static'
app.secret_key = 'your_secret_key'

db = connect.connect_mongo()

DEFAULT_WORDLIST = "/usr/share/dirb/wordlists/common.txt"

def run_dirb(url, wordlist=DEFAULT_WORDLIST):
    command = ["/usr/local/bin/dirb", url, wordlist]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        decoded_output = output.decode('utf-8', 'ignore')
        return [line.split()[1] for line in decoded_output.splitlines() if line.startswith("[+]")]
    except subprocess.CalledProcessError as e:
        print(f"Error al escanear {url}: {e.output.decode() if e.output else e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

def save_discovered_routes(url):
    discovered_routes = run_dirb(url)
    if discovered_routes:
        routes_collection = db["routes"]
        data_collection = db["data"]
        for route in discovered_routes:
            try:
                response = requests.get(route, timeout=10)  # Agregar timeout
                routes_collection.insert_one({"url": url, "route": route})
                data_collection.insert_one({"route": route, "status_code": response.status_code})
            except requests.RequestException as e:
                print(f"Error al acceder a {route}: {e}")
    return discovered_routes

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['query']
        if not url.startswith(('http://', 'https://')):
            return "URL inválida", 400
        thread = Thread(target=save_discovered_routes, args=(url,))
        thread.start()
        return f"Escaneo iniciado para: {url}. Verifique más tarde para los resultados."
    return render_template('index.html')

@app.route('/discover', methods=['POST'])
def discover():
    url = request.form['query']
    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "URL inválida"}), 400
    discovered_routes = save_discovered_routes(url)
    if discovered_routes:
        return jsonify({"message": "Rutas descubiertas y guardadas"})
    else:
        return jsonify({"error": "Error al descubrir rutas"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
