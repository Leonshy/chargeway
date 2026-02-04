"""
Script de debugging para verificar IDs de estaciones y conectores
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.estaciones import Station
from models.conectores import Connector
import requests


def verificar_estaciones_db():
    """Muestra las estaciones en la base de datos"""
    print("\n" + "=" * 60)
    print("ESTACIONES EN LA BASE DE DATOS")
    print("=" * 60 + "\n")

    estaciones = Station.query.all()

    for est in estaciones[:10]:  # Mostrar solo las primeras 10
        conectores = Connector.query.filter_by(estacion_id=est.id).all()
        print(f"ID: {est.id}")
        print(f"Nombre: {est.nombre}")
        print(f"Dirección: {est.direccion}")
        print(f"Conectores: {len(conectores)}")
        if conectores:
            for c in conectores:
                print(f"  - {c.nombre} ({c.tipo}, {c.potencia_kw} kW)")
        print()


def verificar_estaciones_openchargemap():
    """Muestra las estaciones de OpenChargeMap"""
    print("\n" + "=" * 60)
    print("ESTACIONES DE OPENCHARGEMAP (API)")
    print("=" * 60 + "\n")

    url = "https://api.openchargemap.io/v3/poi/"
    params = {
        "output": "json",
        "countrycode": "PY",
        "maxresults": 10,
        "compact": True,
        "verbose": False,
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 403:
            print("⚠️ Error 403: OpenChargeMap requiere API Key")
            print(
                "\nSolución: Necesitas registrarte en OpenChargeMap para obtener una API key"
            )
            print("1. Visita: https://openchargemap.org/site/develop/register")
            print("2. Registra una cuenta")
            print("3. Obtén tu API key")
            print("4. Agrega '&key=TU_API_KEY' a los parámetros\n")
            return

        response.raise_for_status()
        estaciones = response.json()

        for est in estaciones[:10]:
            info = est.get("AddressInfo", {})
            print(f"ID OpenChargeMap: {est.get('ID')}")
            print(f"Nombre: {info.get('Title', 'Sin nombre')}")
            print(f"Dirección: {info.get('AddressLine1', 'Sin dirección')}")
            connections = est.get("Connections", [])
            print(f"Conectores: {len(connections)}")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")


def comparar_ids():
    """Compara IDs entre DB y OpenChargeMap"""
    print("\n" + "=" * 60)
    print("COMPARACIÓN DE IDs")
    print("=" * 60 + "\n")

    # IDs en la base de datos
    estaciones_db = Station.query.all()
    ids_db = {est.id: est.nombre for est in estaciones_db}

    print(f"IDs en la base de datos: {sorted(ids_db.keys())[:10]}...")
    print(f"Total: {len(ids_db)}\n")

    # Verificar si algún ID está en un rango típico de OpenChargeMap
    ids_grandes = [id for id in ids_db.keys() if id > 1000]

    if ids_grandes:
        print("✅ Algunos IDs parecen ser de OpenChargeMap (>1000)")
        print(f"   Ejemplos: {ids_grandes[:5]}")
    else:
        print("⚠️ Todos los IDs son pequeños (<1000)")
        print("   Esto sugiere que son IDs autogenerados, no de OpenChargeMap")
        print("\n🔥 ESTE ES PROBABLEMENTE TU PROBLEMA:")
        print("   - El frontend usa IDs de OpenChargeMap (ej: 12345)")
        print("   - El backend tiene IDs autogenerados (ej: 1, 2, 3)")
        print("   - Por eso no encuentra los conectores\n")


def verificar_estacion_especifica(estacion_id):
    """Verifica una estación específica"""
    print(f"\n" + "=" * 60)
    print(f"VERIFICANDO ESTACIÓN ID: {estacion_id}")
    print("=" * 60 + "\n")

    estacion = Station.query.get(estacion_id)

    if not estacion:
        print(f"❌ No existe una estación con ID {estacion_id} en la base de datos")
        print("\nEstaciones disponibles:")
        for est in Station.query.limit(5).all():
            print(f"  - ID {est.id}: {est.nombre}")
        return

    print(f"✅ Estación encontrada:")
    print(f"   Nombre: {estacion.nombre}")
    print(f"   Dirección: {estacion.direccion}")
    print(f"   Lat/Lon: {estacion.lat}, {estacion.lon}\n")

    conectores = Connector.query.filter_by(estacion_id=estacion_id).all()
    print(f"🔌 Conectores: {len(conectores)}")

    if conectores:
        for c in conectores:
            print(f"   - {c.nombre}")
            print(f"     Tipo: {c.tipo}")
            print(f"     Potencia: {c.potencia_kw} kW")
            print(f"     Activo: {c.activo}")
            print()
    else:
        print("   ⚠️ No hay conectores para esta estación")


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 60)
        print("HERRAMIENTA DE DEBUGGING - ESTACIONES Y CONECTORES")
        print("=" * 60)

        # 1. Verificar estaciones en DB
        verificar_estaciones_db()

        # 2. Comparar IDs
        comparar_ids()

        # 3. Verificar estaciones de OpenChargeMap
        print("\nIntentando obtener estaciones de OpenChargeMap...")
        verificar_estaciones_openchargemap()

        # 4. Prueba con una estación específica
        print("\n" + "=" * 60)
        estacion_test = input(
            "Ingresa un ID de estación para verificar (o Enter para salir): "
        ).strip()

        if estacion_test:
            try:
                verificar_estacion_especifica(int(estacion_test))
            except ValueError:
                print("❌ Debes ingresar un número")
