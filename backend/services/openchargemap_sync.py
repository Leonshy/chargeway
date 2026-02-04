"""
openchargemap_sync.py
---------------------
Este módulo se encarga de:
1) Consultar OpenChargeMap para Paraguay (countrycode=PY) con paginación
2) Insertar/Actualizar estaciones en la tabla "stations"
3) Insertar/Actualizar conectores en la tabla "connectors"

Se usa como SEED temporal desde la consola Python:
    from app import app
    from services.openchargemap_sync import sync_openchargemap_paraguay

    with app.app_context():
        print(sync_openchargemap_paraguay(reset=True, maxresults=200))
"""

import os
import hashlib
import requests

from db import db
from models.estaciones import Station
from models.conectores import Connector


def _stable_int(key: str) -> int:
    """
    Genera un entero estable (repetible) a partir de un string.
    Lo usamos para crear IDs de conectores cuando la API no trae un ID único usable.
    """
    # MD5 -> tomamos 8 hex (32 bits) -> int
    h = hashlib.md5(key.encode("utf-8")).hexdigest()[:8]
    return int(h, 16)


def _get_api_key() -> str | None:
    """
    Busca una API key de OpenChargeMap:
    - Primero en .env como OPENCHARGEMAP_API_KEY
    - Si no existe, intenta tomar la constante API_KEY desde services.openchargemap (si tu archivo la tiene)
    """
    # 1) Desde .env
    key = os.getenv("OPENCHARGEMAP_API_KEY")
    if key:
        return key

    # 2) Fallback: si existe API_KEY en services/openchargemap.py
    try:
        from services.openchargemap import API_KEY  # type: ignore
        return API_KEY
    except Exception:
        return None


def _fetch_page(countrycode: str, maxresults: int, offset: int) -> list:
    """
    Trae una "página" de estaciones desde OpenChargeMap.
    """
    url = "https://api.openchargemap.io/v3/poi/"
    api_key = _get_api_key()

    # Parámetros para traer data del país + paginación
    params = {
        "output": "json",
        "countrycode": countrycode,
        "compact": "true",     # payload más liviano
        "verbose": "false",
        "maxresults": maxresults,
        "offset": offset,
    }

    # OpenChargeMap acepta key como parámetro (compatibilidad)
    if api_key:
        params["key"] = api_key

    # Pedimos con timeout para evitar cuelgues
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()

    data = resp.json()

    # Aseguramos lista
    return data if isinstance(data, list) else []


def _build_station_fields(poi: dict) -> dict | None:
    """
    Extrae campos para la tabla stations desde un POI de OpenChargeMap.
    Retorna un dict listo para Station(...)
    """
    station_id = poi.get("ID")
    address = poi.get("AddressInfo") or {}

    lat = address.get("Latitude")
    lon = address.get("Longitude")
    nombre = address.get("Title") or f"Estación {station_id}"

    # Construimos dirección legible
    # AddressLine1 + Town + StateOrProvince
    parts = []
    if address.get("AddressLine1"):
        parts.append(address["AddressLine1"])
    if address.get("Town"):
        parts.append(address["Town"])
    if address.get("StateOrProvince"):
        parts.append(address["StateOrProvince"])

    direccion = ", ".join(parts).strip() if parts else "Sin dirección"

    # Validamos mínimos indispensables
    if not station_id or lat is None or lon is None:
        return None

    return {
        "id": int(station_id),     # usamos el ID de OpenChargeMap como PK para evitar duplicados
        "nombre": str(nombre)[:120],
        "direccion": str(direccion)[:200],
        "lat": float(lat),
        "lon": float(lon),
    }

def _tipo_corto(tipo_largo: str) -> str:
    """
    Convierte un tipo largo de OpenChargeMap a un tipo corto para guardar en VARCHAR(20).
    """
    t = (tipo_largo or "").lower()

    if "ccs" in t:
        return "CCS"
    if "chademo" in t:
        return "CHAdeMO"
    if "type 2" in t:
        return "Type 2"
    if "type 1" in t:
        return "Type 1"
    if "tesla" in t:
        return "Tesla"

    # Fallback: recortamos a 20 caracteres para que entre en la columna
    return (tipo_largo.strip()[:20] if tipo_largo else "Desconocido")

def _build_connectors(poi: dict) -> list[Connector]:
    """
    Construye lista de objetos Connector desde el POI.
    Respeta:
    - connectors.id (PK) debe ser único
    - tipo es NOT NULL (si falta, ponemos 'Desconocido')
    - potencia_kw es NOT NULL (si falta, ponemos 0.0)
    """
    station_id = poi.get("ID")
    connections = poi.get("Connections") or []

    if not station_id:
        return []

    station_id = int(station_id)

    nuevos: list[Connector] = []

    for idx, c in enumerate(connections):
        # Cantidad de conectores físicos del mismo tipo (si la API lo trae)
        quantity = c.get("Quantity") or 1
        try:
            quantity = int(quantity)
        except Exception:
            quantity = 1

        # Tipo: preferimos el título del ConnectionType
        ct = c.get("ConnectionType") or {}
        tipo = None
        # 1) Si viene el objeto con Title, usamos eso (lo correcto)
        if isinstance(ct, dict):
            title = ct.get("Title")
            if title:
                tipo = str(title).strip()

        # 2) Si por alguna razón no viene Title, usamos ConnectionTypeID como fallback
        if not tipo and c.get("ConnectionTypeID") is not None:
            tipo = f"TYPE_ID_{c.get('ConnectionTypeID')}"

        # 3) Último fallback (raro)
        if not tipo:
            tipo = "Desconocido"

        # Potencia en kW
        potencia = c.get("PowerKW")
        try:
            potencia_kw = float(potencia) if potencia is not None else 0.0
        except Exception:
            potencia_kw = 0.0

        # ID original del conector si existe
        conn_id = c.get("ID")

        # Si quantity > 1, creamos varios conectores (para permitir reservas simultáneas reales)
        for i in range(quantity):
            # Nombre visible del conector (ej: "Type 2 - 22kW #1")
            nombre = f"{tipo} - {int(potencia_kw)}kW #{i+1}"

            # Generamos PK estable:
            # - si hay conn_id y quantity==1, usamos ese ID tal cual (más simple)
            # - si no, generamos un entero estable con md5
            if conn_id and quantity == 1:
                connector_pk = int(conn_id)
            else:
                key = f"{station_id}:{conn_id or idx}:{i}:{tipo}:{potencia_kw}"
                connector_pk = _stable_int(key)

            nuevos.append(
                Connector(
                    id=connector_pk,
                    estacion_id=station_id,
                    nombre=nombre[:50],
                    tipo=_tipo_corto(tipo),          # tu columna tipo es VARCHAR(20) NOT NULL
                    potencia_kw=potencia_kw,
                    activo=True,
                )
            )

    return nuevos


def sync_openchargemap_paraguay(reset: bool = False, maxresults: int = 200) -> dict:
    """
    Sincroniza estaciones y conectores de Paraguay desde OpenChargeMap a SQLite.

    reset=True:
      - Borra stations y connectors antes de cargar (útil para seed limpio)

    maxresults:
      - Tamaño de cada página (200 es estable; 500/1000 puede depender del rate limit)
    """
    countrycode = "PY"

    # Contadores para reporte final
    inserted_stations = 0
    updated_stations = 0
    total_connectors = 0
    errors = 0

    # Si pedimos reset, borramos primero
    if reset:
        try:
            # Primero conectores, luego estaciones (por orden lógico)
            Connector.query.delete()
            Station.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": f"Reset falló: {e}"}

    offset = 0

    while True:
        try:
            batch = _fetch_page(countrycode=countrycode, maxresults=maxresults, offset=offset)
        except Exception as e:
            errors += 1
            break

        if not batch:
            # ya no hay más datos
            break

        for poi in batch:
            try:
                # 1) Armamos datos de estación
                fields = _build_station_fields(poi)
                if not fields:
                    continue

                station_id = fields["id"]

                # 2) Upsert estación (insert o update)
                existing = db.session.get(Station, station_id)
                if existing:
                    existing.nombre = fields["nombre"]
                    existing.direccion = fields["direccion"]
                    existing.lat = fields["lat"]
                    existing.lon = fields["lon"]
                    updated_stations += 1
                else:
                    db.session.add(Station(**fields))
                    inserted_stations += 1

                # 3) Conectores: evitamos duplicados borrando los de esa estación y recargando
                Connector.query.filter_by(estacion_id=station_id).delete()

                nuevos = _build_connectors(poi)
                if nuevos:
                    db.session.add_all(nuevos)
                    total_connectors += len(nuevos)

            except Exception:
                errors += 1
                db.session.rollback()
                continue

        # Commit por lote (más seguro que al final, por si hay muchos datos)
        try:
            db.session.commit()
        except Exception:
            errors += 1
            db.session.rollback()

        # Si vino menos que maxresults, probablemente ya terminamos
        if len(batch) < maxresults:
            break

        offset += maxresults

    return {
        "ok": True,
        "inserted_stations": inserted_stations,
        "updated_stations": updated_stations,
        "total_connectors": total_connectors,
        "errors": errors,
        "last_offset": offset,
    }
