from flask import Blueprint, request, jsonify, current_app
import sqlite3
import os

admin_bp = Blueprint('admin_bp', __name__)

# Mapeo de nombres "amigables" a archivos físicos y tablas
DB_MAP = {
    'usuarios': {'file': 'users.db', 'table': 'users'},
    'estaciones': {'file': 'station.db', 'table': 'station'},
    'reservas': {'file': 'reservas.db', 'table': 'reservas'},
    'vehiculos': {'file': 'vehiculos_ev.db', 'table': 'vehiculos'} 
}

def get_db_connection(db_filename):
    # Conecta a la base de datos específica dentro de /instance
    db_path = os.path.join(current_app.instance_path, db_filename)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# 1. LISTAR TABLAS DISPONIBLES
@admin_bp.route('/tables', methods=['GET'])
def list_tables():
    return jsonify(list(DB_MAP.keys()))

# 2. OBTENER DATOS (READ)
@admin_bp.route('/data/<target>', methods=['GET'])
def get_data(target):
    if target not in DB_MAP:
        return jsonify({'error': 'Base de datos no encontrada'}), 404
    
    conf = DB_MAP[target]
    try:
        conn = get_db_connection(conf['file'])
        # Obtenemos todo de la tabla
        rows = conn.execute(f"SELECT * FROM {conf['table']}").fetchall()
        conn.close()
        
        # Convertimos a lista de diccionarios
        data = [dict(row) for row in rows]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 3. AGREGAR DATO (CREATE)
@admin_bp.route('/data/<target>', methods=['POST'])
def add_data(target):
    if target not in DB_MAP: return jsonify({'error': 'Target inválido'}), 404
    
    conf = DB_MAP[target]
    data = request.json # Datos enviados desde el frontend
    
    try:
        conn = get_db_connection(conf['file'])
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        values = list(data.values())
        
        query = f"INSERT INTO {conf['table']} ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)
        conn.commit()
        conn.close()
        return jsonify({'message': 'Dato agregado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 4. MODIFICAR DATO (UPDATE)
@admin_bp.route('/data/<target>/<int:id>', methods=['PUT'])
def update_data(target, id):
    if target not in DB_MAP: return jsonify({'error': 'Target inválido'}), 404
    
    conf = DB_MAP[target]
    data = request.json
    
    try:
        conn = get_db_connection(conf['file'])
        
        # Construir query dinámico: "col1=?, col2=?"
        updates = ', '.join([f"{k}=?" for k in data.keys()])
        values = list(data.values())
        values.append(id) # El ID va al final para el WHERE
        
        query = f"UPDATE {conf['table']} SET {updates} WHERE id=?"
        conn.execute(query, values)
        conn.commit()
        conn.close()
        return jsonify({'message': 'Dato actualizado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 5. ELIMINAR DATO (DELETE)
@admin_bp.route('/data/<target>/<int:id>', methods=['DELETE'])
def delete_data(target, id):
    if target not in DB_MAP: return jsonify({'error': 'Target inválido'}), 404
    
    conf = DB_MAP[target]
    try:
        conn = get_db_connection(conf['file'])
        conn.execute(f"DELETE FROM {conf['table']} WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Dato eliminado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500