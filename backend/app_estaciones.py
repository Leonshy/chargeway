from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Regístrate en openchargemap.org para obtener tu Key gratis.
# Si no tienes una, a veces funciona sin ella para pruebas limitadas, pero es mejor ponerla.
OCM_API_KEY = 'f10c79d2-e68d-423c-ac00-d318a2845c78' 

@app.route('/mapa')
def ver_mapa():
    return render_template('mapa.html') # CAMBIA ESTO por el nombre correcto de tu plantilla HTML

@app.route('/api/estaciones')
def obtener_estaciones():
    # Coordenadas (Paraguay/Asunción como referencia)
    lat = -25.2867
    lon = -57.6470
    
    url = "https://api.openchargemap.io/v3/poi/"
    
    params = {
        "output": "json",
        "countrycode": "PY",
        "latitude": lat,
        "longitude": lon,
        "distance": 200,          # Aumenté el radio a 200km para ver más
        "distanceunit": "KM",
        "maxresults": 100,
        "compact": False,         # <--- IMPORTANTE: False para ver nombres completos
        "verbose": False,
        "key": OCM_API_KEY        # Asegúrate de poner tu KEY arriba
    }
    
    # Es buena práctica añadir un User-Agent
    headers = {
        'User-Agent': 'MiAppVehiculosEV/1.0'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})
        

if __name__ == '__main__':
    app.run(debug=True) 