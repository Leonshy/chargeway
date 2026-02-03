from flask import Blueprint, request, jsonify, current_app
import sqlite3
import os

admin_bp = Blueprint('admin_bp', __name__)

# Configuración de las bases de datos
# NOTA: Verifica que el nombre de 'table' coincida con tu base de datos
DB_MAP = {
    'usuarios': {'file': 'users.db', 'table': 'user'},    # Cambiado a 'user' (común en SQLAlchemy)
    'estaciones': {'file': 'station.db', 'table': 'stations'},
    'reservas': {'file': 'reservas.db', 'table': 'reservas'},
    'vehiculos': {'file': 'vehiculos_ev.db', 'table': 'autos'},
    'conectores': {'file': 'conectores.db', 'table': 'conectores'}
}

def get_db_connection(db_filename):
    # Localizamos la carpeta 'instance' de forma absoluta
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'instance', db_filename)
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Archivo no encontrado en: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Esto permite traer los datos como diccionarios
    return conn

@admin_bp.route('/tables', methods=['GET'])
def list_tables():
    return jsonify(list(DB_MAP.keys()))

@admin_bp.route('/data/<target>', methods=['GET'])
def get_data(target):
    if target not in DB_MAP:
        return jsonify({'error': 'Configuración de base de datos no encontrada'}), 404
    
    conf = DB_MAP[target]
    try:
        conn = get_db_connection(conf['file'])
        cursor = conn.cursor()

        # Intentamos traer TODOS los datos de la tabla configurada
        try:
            query = f"SELECT * FROM {conf['table']}"
            rows = cursor.execute(query).fetchall()
        except sqlite3.OperationalError:
            # Si falla (ej: la tabla no se llama 'users' sino 'user'), 
            # buscamos automáticamente el nombre correcto de la tabla.
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas_reales = [t[0] for t in cursor.fetchall() if t[0] != 'sqlite_sequence']
            
            return jsonify({
                'error': f"La tabla '{conf['table']}' no existe.",
                'tablas_encontradas': tablas_reales,
                'ayuda': f"Cambia el nombre en DB_MAP a una de estas: {tablas_reales}"
            }), 500

        conn.close()
        
        # Convertimos los objetos Row a diccionarios puros
        data = [dict(row) for row in rows]
        return jsonify(data)

    except Exception as e:
        print(f"❌ Error en Admin: {e}")
        return jsonify({'error': str(e)}), 500

# Rutas para Crear, Modificar y Eliminar (se mantienen igual de dinámicas)
@admin_bp.route('/data/<target>', methods=['POST'])
def add_data(target):
    conf = DB_MAP[target]
    data = request.json
    try:
        conn = get_db_connection(conf['file'])
        columnas = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {conf['table']} ({columnas}) VALUES ({placeholders})"
        conn.execute(query, list(data.values()))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Agregado correctamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/data/<target>/<int:id>', methods=['DELETE'])
def delete_data(target, id):
    conf = DB_MAP[target]
    try:
        conn = get_db_connection(conf['file'])
        conn.execute(f"DELETE FROM {conf['table']} WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Eliminado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500