from db import db
from sqlalchemy import text


def agregar_columna_conector_id():
    print("=" * 70)
    print("🔧 AGREGANDO COLUMNA conector_id A LA TABLA reservas")
    print("=" * 70)

    inspector = db.inspect(db.engine)
    columns = [col["name"] for col in inspector.get_columns("reservas")]

    if "conector_id" in columns:
        print("✅ La columna conector_id ya existe")
        return

    with db.engine.connect() as conn:
        conn.execute(text("ALTER TABLE reservas ADD COLUMN conector_id INTEGER"))
        conn.commit()

    print("✅ Columna conector_id agregada exitosamente")


if __name__ == "__main__":
    print("❌ No ejecutes este archivo directamente")
