import os
from flask import Flask, render_template, jsonify, request
import sqlite3

# Configuración para que busque la base de datos en la carpeta 'instance'
app = Flask(__name__, instance_relative_config=True)

def get_db():
    # Ruta robusta a la base de datos
    db_path = os.path.join(app.instance_path, 'vehiculos_ev.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

# Función auxiliar para quitar acentos de las llaves del JSON
# Esto hace que en JS uses 'data.bateria' en vez de 'data["batería"]'
def limpiar_llaves(fila_db):
    d = dict(fila_db)
    nuevo_dict = {}
    for key, value in d.items():
        # Reemplazos comunes
        new_key = key.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        # Reemplazo específico para tu columna nueva
        new_key = new_key.replace('puerto_de_carga', 'puerto') 
        nuevo_dict[new_key] = value
    return nuevo_dict

@app.route('/')
def inicio():
    return render_template('index.html')

# API 1: Marcas
@app.route('/api/marcas')
def get_marcas():
    conn = get_db()
    rows = conn.execute('SELECT DISTINCT marca FROM autos ORDER BY marca').fetchall()
    conn.close()
    marcas = [row['marca'] for row in rows]
    return jsonify(marcas)

# API 2: Modelos
@app.route('/api/modelos/<marca>')
def get_modelos(marca):
    conn = get_db()
    rows = conn.execute('SELECT modelo FROM autos WHERE marca = ? ORDER BY modelo', (marca,)).fetchall()
    conn.close()
    modelos = [row['modelo'] for row in rows]
    return jsonify(modelos)

# API 3: Detalle (Aquí es donde incluimos los nuevos datos)
@app.route('/api/detalle')
def get_detalle():
    marca = request.args.get('marca')
    modelo = request.args.get('modelo')
    
    conn = get_db()
    # Usamos SELECT * para traer automáticamente las nuevas columnas (puerto, autonomia, etc.)
    auto = conn.execute('SELECT * FROM autos WHERE marca = ? AND modelo = ?', (marca, modelo)).fetchone()
    conn.close()
    
    if auto:
        # Convertimos y limpiamos los acentos antes de enviar
        datos_limpios = limpiar_llaves(auto)
        return jsonify(datos_limpios)
    
    return jsonify({'error': 'Auto no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)