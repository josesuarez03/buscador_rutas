from flask import Flask, render_template, request, jsonify
import subprocess
import pymongo
import requests
from threading import Thread

app =  Flask(__name__)

app.static_folder = 'static'
app.secret_key = 'your_secret_key'

# Conexión a MongoDB
client = pymongo.MongoClient("mongodb://db:27017/")
db = client["web_scraping"]
routes_collection = db["routes"]
data_collection = db["data"]

DEFAULT_WORDLIST = "/usr/share/dirb/wordlists/common.txt"

def discover_routes(url, wordlist=DEFAULT_WORDLIST):
    try:
        output = subprocess.check_output(["/usr/local/bin/dirb", url, wordlist])
        return [line.split()[1] for line in output.decode().splitlines() if line.startswith("[+]")]
    except subprocess.CalledProcessError as e:
        print(f"Error al escanear {url}: {e}")
        return None

@app.route( '/', methods=['GET',  'POST'] )
def index():
    if request.method == 'POST':
        url = request.form['query']
        thread = Thread(target=discover_routes, args=(url,))
        thread.start()
        return f"Escaneo iniciado para: {url}. Verifique más tarde para los resultados."
    return  render_template('index.html')

@app.route('/discover', methods=['POST'])
def discover():
    url = request.form['query']
    discovered_routes = discover_routes(url)

    if discovered_routes:
        for route in discovered_routes:
            data.insert_route(route)
            response = requests.get(route)
            data.insert_data(route, {"código_estado": response.status_code})   
        return jsonify({"message": "Rutas descubiertas y guardadas"}) 
    else:
        return jsonify({"error": "Error al descubrir rutas"}), 500 

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")