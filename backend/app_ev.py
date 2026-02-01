from flask import Flask, render_template, jsonify, request
import sqlite3
import os

app = Flask(__name__, instance_relative_config=True)

def get_db():
    db_path = os.path.join(app.instance_path, 'vehiculos_ev.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn

@app.route('/')
def inicio():
    return render_template('index.html') # cambia 'index.html' por tu plantilla principal

# API 1: Obtener lista de marcas únicas
@app.route('/api/marcas')
def get_marcas():
    conn = get_db()
    rows = conn.execute('SELECT DISTINCT marca FROM autos ORDER BY marca').fetchall()
    conn.close()
    marcas = [row['marca'] for row in rows]
    return jsonify(marcas)

# API 2: Obtener modelos según la marca seleccionada
@app.route('/api/modelos/<marca>')
def get_modelos(marca):
    conn = get_db()
    rows = conn.execute('SELECT modelo FROM autos WHERE marca = ? ORDER BY modelo', (marca,)).fetchall()
    conn.close()
    modelos = [row['modelo'] for row in rows]
    return jsonify(modelos)

# API 3: Obtener detalles completos de un auto específico
@app.route('/api/detalle')
def get_detalle():
    marca = request.args.get('marca')
    modelo = request.args.get('modelo')
    
    conn = get_db()
    auto = conn.execute('SELECT * FROM autos WHERE marca = ? AND modelo = ?', (marca, modelo)).fetchone()
    conn.close()
    
    if auto:
        # Convertimos el objeto Row a un diccionario normal
        return jsonify(dict(auto))
    return jsonify({'error': 'Auto no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)