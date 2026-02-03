import requests
import folium

API_KEY = "f10c79d2-e68d-423c-ac00-d318a2845c78"  # Reemplaza con tu API Key real de OpenChargeMap


def obtener_estaciones():
    try:
        url = "https://api.openchargemap.io/v3/poi/"
        params = {"countrycode": "PY", "maxresults": 50, "key": API_KEY}
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error al obtener estaciones: {e}")
        return []


def generar_mapa():
    estaciones = obtener_estaciones()
    mapa = folium.Map(location=[-23.442503, -58.443832], zoom_start=6)

    for e in estaciones:
        info = e.get("AddressInfo")
        if info:
            lat = info.get("Latitude")
            lon = info.get("Longitude")
            title = info.get("Title", "Estación")
            if lat and lon:
                folium.Marker(
                    [lat, lon],
                    popup=f"<b>{title}</b><br>{info.get('AddressLine1','')}",
                    icon=folium.Icon(color="green", icon="bolt", prefix="fa"),
                ).add_to(mapa)

    return mapa._repr_html_()
