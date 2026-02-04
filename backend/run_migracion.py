from app import app
from migracion import agregar_columna_conector_id

with app.app_context():
    agregar_columna_conector_id()
