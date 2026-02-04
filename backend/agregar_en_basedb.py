"""
Script de Migración: Agregar Sistema de Roles
==============================================

Este script agrega el campo 'role' a la tabla de usuarios
y crea el primer usuario administrador.

Uso:
    python migrate_add_roles.py
"""

import sqlite3
import os
from pathlib import Path

# Configuración
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DB_PATH = INSTANCE_DIR / "chargeway.db"


def migrate():
    """Ejecutar la migración"""
    print("🔧 Iniciando migración de roles...")

    if not DB_PATH.exists():
        print(f"❌ Error: Base de datos no encontrada en {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Paso 1: Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if "role" in columns:
            print("⚠️  La columna 'role' ya existe. Saltando este paso...")
        else:
            # Paso 2: Agregar columna 'role' con valor por defecto 'user'
            print("📝 Agregando columna 'role' a la tabla users...")
            cursor.execute(
                """
                ALTER TABLE users 
                ADD COLUMN role TEXT NOT NULL DEFAULT 'user'
            """
            )
            print("✅ Columna 'role' agregada exitosamente")

        # Paso 3: Verificar si existe algún admin
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]

        if admin_count == 0:
            print("\n🔑 No hay administradores en el sistema.")
            print("Vamos a crear el primer usuario administrador...\n")

            # Mostrar usuarios existentes
            cursor.execute("SELECT id, username, email FROM users")
            users = cursor.fetchall()

            if users:
                print("Usuarios existentes:")
                for user in users:
                    print(f"  [{user[0]}] {user[1]} - {user[2]}")

                print("\nOpciones:")
                print("1. Promover un usuario existente a admin")
                print("2. Crear un nuevo usuario admin")

                choice = input("\nSelecciona una opción (1 o 2): ").strip()

                if choice == "1":
                    # Promover usuario existente
                    user_id = input("Ingresa el ID del usuario a promover: ").strip()
                    cursor.execute(
                        "UPDATE users SET role = 'admin' WHERE id = ?", (user_id,)
                    )
                    print(f"✅ Usuario ID {user_id} promovido a administrador")

                elif choice == "2":
                    # Crear nuevo admin
                    from werkzeug.security import generate_password_hash

                    username = input("Nombre de usuario admin: ").strip()
                    email = input("Email del admin: ").strip()
                    password = input("Contraseña: ").strip()

                    password_hash = generate_password_hash(password)

                    cursor.execute(
                        """
                        INSERT INTO users (username, email, password_hash, role, is_active)
                        VALUES (?, ?, ?, 'admin', 1)
                    """,
                        (username, email, password_hash),
                    )

                    print(f"✅ Usuario admin '{username}' creado exitosamente")

                else:
                    print("❌ Opción inválida")
            else:
                # No hay usuarios, crear el primero como admin
                from werkzeug.security import generate_password_hash

                print("No hay usuarios en el sistema. Creando el primer admin...")
                username = input("Nombre de usuario admin: ").strip() or "admin"
                email = input("Email del admin: ").strip() or "admin@chargeway.com"
                password = input("Contraseña: ").strip() or "admin123"

                password_hash = generate_password_hash(password)

                cursor.execute(
                    """
                    INSERT INTO users (username, email, password_hash, role, is_active)
                    VALUES (?, ?, ?, 'admin', 1)
                """,
                    (username, email, password_hash),
                )

                print(f"✅ Usuario admin '{username}' creado exitosamente")

        else:
            print(f"✅ Ya existe(n) {admin_count} administrador(es) en el sistema")

        # Commit de cambios
        conn.commit()

        # Mostrar resumen
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        stats = cursor.fetchall()

        print("\n📊 Resumen de usuarios:")
        for role, count in stats:
            print(f"  {role}: {count}")

        print("\n✅ Migración completada exitosamente!")
        return True

    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def rollback():
    """Revertir la migración (opcional)"""
    print("🔙 Revirtiendo migración...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # SQLite no soporta DROP COLUMN directamente
        # Necesitamos recrear la tabla sin la columna
        print("⚠️  SQLite no soporta eliminar columnas fácilmente.")
        print("Para revertir, necesitarías restaurar un backup de la base de datos.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Agregar Sistema de Roles")
    print("=" * 60)
    print()

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()

    print("\n" + "=" * 60)
