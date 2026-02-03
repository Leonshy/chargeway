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
    # Coordenadas de Paseo La Galería
    lat, lon = -25.2844487, -57.5631777
    mapa = folium.Map(location=[lat, lon], zoom_start=15)

    map_id = mapa.get_name()

    script_marcador = f"""
    <script>
        var marcador_usuario = null;
        
        function inicializarClic() {{
            // Verificamos si el objeto mapa ya existe en el navegador
            if (typeof {map_id} !== 'undefined') {{
                
                // Escuchar el evento click
                {map_id}.on('click', function(e) {{
                    // Si ya hay un marcador, lo borramos para que solo quede uno
                    if (marcador_usuario) {{
                        {map_id}.removeLayer(marcador_usuario);
                    }}
                    
                    // Crear el nuevo marcador donde se hizo clic
                    marcador_usuario = L.marker(e.latlng).addTo({map_id});
                    
                    // Mostrar popup con coordenadas
                    marcador_usuario.bindPopup(
                        "<b>Ubicación seleccionada</b><br>" + 
                        e.latlng.lat.toFixed(5) + ", " + e.latlng.lng.toFixed(5)
                    ).openPopup();
                }});

            }} else {{
                // Si el mapa aún no carga, reintentamos en 100ms
                setTimeout(inicializarClic, 100);
            }}
        }}

        // Iniciamos el script
        setTimeout(inicializarClic, 500);
    </script>
    """
    
    # Inyectamos el script en el HTML del mapa
    mapa.get_root().html.add_child(folium.Element(script_marcador))

    estaciones = obtener_estaciones()
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
