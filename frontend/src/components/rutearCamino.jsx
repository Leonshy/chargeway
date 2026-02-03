// frontend/src/components/RutearCamino.jsx
import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet-routing-machine';
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';

const RutearCamino = ({ inicio, fin }) => {
    const map = useMap();

    useEffect(() => {
        if (!map || !inicio || !fin) return;

        const routingControl = L.Routing.control({
            waypoints: [
                L.latLng(inicio.lat, inicio.lng),
                L.latLng(fin.lat, fin.lng)
            ],
            routeWhileDragging: false,
            // Opciones visuales de la línea
            lineOptions: {
                styles: [{ color: '#007bff', opacity: 0.7, weight: 6 }]
            },
            // IMPORTANTE: createMarker retorna null para NO poner marcadores extra
            // (usamos los tuyos personalizados)
            createMarker: function() { return null; },
            
            // Ocultar el panel de instrucciones (texto) para que no tape el mapa
            // Si quieres ver las instrucciones (doble derecha, etc), ponlo en true
            show: false, 
            addWaypoints: false,
            draggableWaypoints: false,
            fitSelectedRoutes: false,
            showAlternatives: false
        }).addTo(map);

        // Limpieza al desmontar o cambiar destino
        return () => {
            try {
                map.removeControl(routingControl);
            } catch (e) {
                console.log("Error limpiando ruta", e);
            }
        };
    }, [map, inicio, fin]);

    return null;
};

export default RutearCamino;