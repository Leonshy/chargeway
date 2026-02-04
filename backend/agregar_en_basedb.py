"""
Script de Migración - Agregar campos de Kiosk a Reservas
=========================================================

Este script agrega los nuevos campos necesarios para el sistema de kiosk:
- hora_inicio_real
- hora_fin_real
- conector_id
- duracion_real_horas

IMPORTANTE: Ejecutar este script ANTES de actualizar el modelo en producción.

Uso:
    python agregar_campos_kiosk.py
"""

from db import db
from app import app  # Importa tu aplicación Flask
from sqlalchemy import text


def migrate_reservas_table():
    """Agregar nuevos campos a la tabla reservas"""

    with app.app_context():
        try:
            print("🔧 Iniciando migración de base de datos...")

            # Verificar si las columnas ya existen
            inspector = db.inspect(db.engine)
            columns = [col["name"] for col in inspector.get_columns("reservas")]

            migrations = []

            # Verificar y agregar cada campo
            if "hora_inicio_real" not in columns:
                migrations.append(
                    "ALTER TABLE reservas ADD COLUMN hora_inicio_real TIMESTAMP NULL"
                )
                print("  ✅ Agregando columna: hora_inicio_real")

            if "hora_fin_real" not in columns:
                migrations.append(
                    "ALTER TABLE reservas ADD COLUMN hora_fin_real TIMESTAMP NULL"
                )
                print("  ✅ Agregando columna: hora_fin_real")

            if "conector_id" not in columns:
                migrations.append(
                    "ALTER TABLE reservas ADD COLUMN conector_id INTEGER NULL"
                )
                print("  ✅ Agregando columna: conector_id")

            if "duracion_real_horas" not in columns:
                migrations.append(
                    "ALTER TABLE reservas ADD COLUMN duracion_real_horas FLOAT NULL"
                )
                print("  ✅ Agregando columna: duracion_real_horas")

            # Ejecutar migraciones
            if migrations:
                for migration in migrations:
                    db.session.execute(text(migration))

                db.session.commit()
                print(
                    f"\n✅ Migración completada exitosamente! ({len(migrations)} campos agregados)"
                )
            else:
                print("\n✅ No se requieren migraciones. Todos los campos ya existen.")

            # Actualizar el enum de estado si es necesario (SQLite no soporta ALTER TYPE)
            print(
                "\n⚠️  NOTA: Asegúrate de que el estado 'en_progreso' esté permitido en tu lógica de aplicación."
            )

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error durante la migración: {str(e)}")
            raise


if __name__ == "__main__":
    migrate_reservas_table()
