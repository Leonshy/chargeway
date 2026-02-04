from flask import Flask
from db import db
from sqlalchemy import MetaData, Table, text
from sqlalchemy.exc import OperationalError

# 🔹 Importar tu aplicación Flask
from app import app  # Ajusta si tu app principal se llama distinto

with app.app_context():
    try:
        metadata = MetaData()
        reservas = Table("reservas", metadata, autoload_with=db.engine)

        # Verificar si la columna ya existe
        if "codigo_enviado" not in reservas.c:
            print("➕ Agregando columna 'codigo_enviado' a la tabla 'reservas'...")
            with db.engine.connect() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE reservas ADD COLUMN codigo_enviado BOOLEAN DEFAULT 0;"
                    )
                )
            print("✅ Columna agregada exitosamente.")
        else:
            print("ℹ️ La columna 'codigo_enviado' ya existe, no se hizo nada.")

    except OperationalError as e:
        print(f"❌ Error al acceder a la tabla: {e}")
