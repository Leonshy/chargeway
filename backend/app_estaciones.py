from flask import Flask, render_template
from flask_cors import CORS
import requests
import folium

app = Flask(__name__)
CORS(app) 

# --- CONFIGURACIÓN ---
OCM_API_KEY = 'f10c79d2-e68d-423c-ac00-d318a2845c78'

@app.route('/')
def ver_mapa():
    # 1. Crear mapa centrado en Asunción
    m = folium.Map(location=[-25.2867, -57.6470], zoom_start=12)
    
    # 2. Obtener el nombre interno del mapa para el JS
    map_id = m.get_name()
    
    # 3. Script para Marcador Único (Corregido y robusto)
    # Usamos setTimeout para que el script espere a que Leaflet termine de cargar el mapa
    script_marcador_unico = f"""
    <script>
        var marcador_usuario = null;
        
        function inicializarClic() {{
            if (typeof {map_id} !== 'undefined') {{
                {map_id}.on('click', function(e) {{
                    // Si ya existe un marcador, lo quitamos
                    if (marcador_usuario) {{
                        {map_id}.removeLayer(marcador_usuario);
                    }}
                    // Creamos el nuevo marcador
                    marcador_usuario = L.marker(e.latlng).addTo({map_id});
                    marcador_usuario.bindPopup("<b>Ubicación seleccionada</b><br>" + 
                                             e.latlng.lat.toFixed(5) + ", " + 
                                             e.latlng.lng.toFixed(5)).openPopup();
                }});
            }} else {{
                // Si el mapa aún no carga, reintentamos en 100ms
                setTimeout(inicializarClic, 100);
            }}
        }}
        
        // Iniciamos la espera del mapa
        setTimeout(inicializarClic, 500);
    </script>
    """
    m.get_root().html.add_child(folium.Element(script_marcador_unico))

    # 4. Traer estaciones de carga (API)
    url = "https://api.openchargemap.io/v3/poi/"
    params = {
        "output": "json",
        "countrycode": "PY",
        "distance": 200,
        "key": OCM_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        estaciones = response.json()

        for e in estaciones:
            if 'AddressInfo' in e:
                lat = e['AddressInfo'].get('Latitude')
                lon = e['AddressInfo'].get('Longitude')
                name = e['AddressInfo'].get('Title', 'Sin nombre')
                if lat and lon:
                    # Marcadores verdes para estaciones
                    folium.Marker(
                        [lat, lon], 
                        popup=name,
                        icon=folium.Icon(color='green', icon='bolt', prefix='fa')
                    ).add_to(m)
    except Exception as ex:
        print("Error al traer estaciones:", ex)

    # 5. Convertir a HTML
    mapa_html = m._repr_html_()
    return render_template('index.html', mapa_html=mapa_html)

if __name__ == '__main__':
    app.run(debug=True, port=5000)