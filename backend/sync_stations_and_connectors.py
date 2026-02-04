"""
Script para sincronizar estaciones y conectores desde OpenChargeMap a la base de datos local.

Ejecutar desde el directorio backend:
    python sync_stations_and_connectors.py

Este script:
1. Obtiene estaciones de carga de Paraguay desde OpenChargeMap
2. Las guarda en la tabla 'stations'
3. Crea conectores en la tabla 'connectors' para cada estación
"""

import sys
import os

# Agregar el directorio actual al path para importar módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from db import db
from models.estaciones import Station
from models.conectores import Connector
import requests


def obtener_estaciones_openchargemap():
    """
    Obtiene estaciones de Paraguay desde OpenChargeMap API.
    """
    url = "https://api.openchargemap.io/v3/poi/"
    params = {
        "output": "json",
        "countrycode": "PY",  # Paraguay
        "maxresults": 100,
        "compact": True,
        "verbose": False,
    }

    print("🔍 Obteniendo estaciones desde OpenChargeMap...")

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        estaciones = response.json()
        print(f"✅ Se obtuvieron {len(estaciones)} estaciones de OpenChargeMap")
        return estaciones
    except Exception as e:
        print(f"❌ Error al obtener estaciones: {e}")
        return []


def sincronizar_estaciones_y_conectores(reset=False):
    """
    Sincroniza estaciones y conectores desde OpenChargeMap a la base de datos.

    Args:
        reset: Si es True, elimina todas las estaciones y conectores antes de sincronizar
    """

    # Obtener estaciones de OpenChargeMap
    estaciones_ocm = obtener_estaciones_openchargemap()

    if not estaciones_ocm:
        print("⚠️ No se obtuvieron estaciones. Saliendo...")
        return

    # Si reset=True, eliminar todas las estaciones y conectores
    if reset:
        print("🗑️ Eliminando estaciones y conectores existentes...")
        Connector.query.delete()
        Station.query.delete()
        db.session.commit()
        print("✅ Datos anteriores eliminados")

    print("\n" + "=" * 60)
    print("SINCRONIZANDO ESTACIONES Y CONECTORES")
    print("=" * 60 + "\n")

    estaciones_creadas = 0
    estaciones_actualizadas = 0
    conectores_creados = 0
    errores = 0

    for est_data in estaciones_ocm:
        try:
            # Extraer información de la estación
            ocm_id = est_data.get("ID")
            info = est_data.get("AddressInfo", {})

            # Validar datos mínimos
            if not info or not info.get("Latitude") or not info.get("Longitude"):
                print(f"⚠️ Estación {ocm_id}: Sin coordenadas, omitiendo...")
                continue

            # Datos de la estación
            nombre = info.get("Title", f"Estación {ocm_id}")
            direccion = info.get("AddressLine1", "Dirección no disponible")
            if info.get("Town"):
                direccion += f", {info['Town']}"
            if info.get("StateOrProvince"):
                direccion += f", {info['StateOrProvince']}"

            lat = float(info["Latitude"])
            lon = float(info["Longitude"])

            # Buscar o crear estación
            estacion = Station.query.get(ocm_id)

            if estacion:
                # Actualizar estación existente
                estacion.nombre = nombre
                estacion.direccion = direccion
                estacion.lat = lat
                estacion.lon = lon
                accion = "actualizada"
                estaciones_actualizadas += 1
            else:
                # Crear nueva estación
                estacion = Station(
                    id=ocm_id,
                    nombre=nombre,
                    direccion=direccion,
                    lat=lat,
                    lon=lon,
                )
                db.session.add(estacion)
                accion = "creada"
                estaciones_creadas += 1

            db.session.flush()  # Para obtener el ID de la estación

            # Procesar conectores
            connections = est_data.get("Connections", [])

            if not connections:
                print(
                    f"⚠️ Estación '{nombre}': Sin conectores, creando conector por defecto..."
                )
                # Crear un conector genérico si no hay información
                conector = Connector(
                    estacion_id=estacion.id,
                    nombre="Conector Principal",
                    tipo="Type 2",
                    potencia_kw=22.0,
                    activo=True,
                )
                db.session.add(conector)
                conectores_creados += 1
            else:
                # Eliminar conectores antiguos de esta estación si es actualización
                if accion == "actualizada":
                    Connector.query.filter_by(estacion_id=estacion.id).delete()

                # Crear conectores desde la información de OpenChargeMap
                for idx, conn in enumerate(connections, start=1):
                    # Extraer tipo de conector
                    tipo_obj = conn.get("ConnectionType", {})
                    tipo = (
                        tipo_obj.get("Title", "Desconocido")
                        if tipo_obj
                        else "Desconocido"
                    )

                    # Extraer potencia
                    potencia = conn.get("PowerKW")
                    if not potencia:
                        level = conn.get("Level", {})
                        potencia = 22.0 if level and level.get("ID") == 2 else 11.0

                    # Nombre del conector
                    nombre_conector = f"Conector {idx} - {tipo}"

                    conector = Connector(
                        estacion_id=estacion.id,
                        nombre=nombre_conector,
                        tipo=tipo,
                        potencia_kw=float(potencia),
                        activo=True,
                    )
                    db.session.add(conector)
                    conectores_creados += 1

            db.session.commit()

            print(f"✅ Estación {accion}: '{nombre}' (ID: {ocm_id})")
            print(f"   📍 {direccion}")
            print(f"   🔌 {len(connections) if connections else 1} conector(es)")
            print()

        except Exception as e:
            db.session.rollback()
            errores += 1
            print(
                f"❌ Error procesando estación {est_data.get('ID', 'desconocido')}: {e}"
            )
            print()

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE SINCRONIZACIÓN")
    print("=" * 60)
    print(f"📊 Estaciones creadas: {estaciones_creadas}")
    print(f"🔄 Estaciones actualizadas: {estaciones_actualizadas}")
    print(f"🔌 Conectores creados: {conectores_creados}")
    print(f"❌ Errores: {errores}")
    print("=" * 60 + "\n")

    if conectores_creados > 0:
        print("✅ ¡Sincronización completada exitosamente!")
        print("\n💡 Ahora puedes hacer reservas desde la aplicación web")
        print("   Las estaciones ahora tienen conectores disponibles")
    else:
        print("⚠️ No se crearon conectores. Verifica la conexión a OpenChargeMap")


def mostrar_estadisticas():
    """
    Muestra estadísticas de la base de datos.
    """
    total_estaciones = Station.query.count()
    total_conectores = Connector.query.count()
    conectores_activos = Connector.query.filter_by(activo=True).count()

    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DE LA BASE DE DATOS")
    print("=" * 60)
    print(f"🏢 Total de estaciones: {total_estaciones}")
    print(f"🔌 Total de conectores: {total_conectores}")
    print(f"✅ Conectores activos: {conectores_activos}")
    print("=" * 60 + "\n")

    if total_estaciones > 0:
        print("📋 Primeras 5 estaciones:")
        for est in Station.query.limit(5).all():
            num_conectores = len(est.connectors)
            print(f"   • {est.nombre} ({num_conectores} conectores)")

    print()


def menu_principal():
    """
    Menú interactivo para el usuario.
    """
    print("\n" + "=" * 60)
    print("SINCRONIZADOR DE ESTACIONES Y CONECTORES")
    print("OpenChargeMap → Base de Datos Local")
    print("=" * 60 + "\n")

    print("Opciones:")
    print("1. Sincronizar (mantener datos existentes)")
    print("2. Sincronizar con RESET (eliminar todo y volver a crear)")
    print("3. Ver estadísticas")
    print("4. Salir")
    print()

    opcion = input("Selecciona una opción (1-4): ").strip()

    return opcion


if __name__ == "__main__":
    # Crear la aplicación Flask
    app = create_app()

    with app.app_context():
        while True:
            opcion = menu_principal()

            if opcion == "1":
                print("\n🔄 Iniciando sincronización (sin reset)...\n")
                sincronizar_estaciones_y_conectores(reset=False)
                mostrar_estadisticas()

            elif opcion == "2":
                confirmacion = (
                    input(
                        "\n⚠️ ¿Estás seguro? Esto eliminará TODAS las estaciones y conectores existentes (s/n): "
                    )
                    .strip()
                    .lower()
                )
                if confirmacion == "s":
                    print("\n🔄 Iniciando sincronización con RESET...\n")
                    sincronizar_estaciones_y_conectores(reset=True)
                    mostrar_estadisticas()
                else:
                    print("❌ Operación cancelada")

            elif opcion == "3":
                mostrar_estadisticas()

            elif opcion == "4":
                print("\n👋 ¡Hasta luego!\n")
                break

            else:
                print("\n❌ Opción inválida. Intenta de nuevo.\n")

            input("\nPresiona ENTER para continuar...")
