import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// --- IMPORTACIÓN NUEVA ---
import RutearCamino from './rutearCamino';

// Fix para los iconos de Leaflet en React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Componente para crear iconos personalizados
const createCustomIcon = (color) => {
    return L.divIcon({
        className: 'custom-marker',
        html: `
      <div style="
        background-color: ${color};
        width: 30px;
        height: 30px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 3px solid white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <i class="fa-solid fa-bolt" style="
          transform: rotate(45deg);
          color: white;
          font-size: 14px;
        "></i>
      </div>
    `,
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30]
    });
};

// --- MODIFICADO: Agregamos 'limpiarRuta' para borrar la línea si el usuario se mueve ---
function MarcadorUsuario({ posicion, setPosicion, limpiarRuta }) {
    useMapEvents({
        click(e) {
            setPosicion(e.latlng); // Guardamos la latitud y longitud del clic
            if (limpiarRuta) limpiarRuta(); // Si mueves tu posición, borramos la ruta vieja
        },
    });

    if (posicion === null) return null;

    return (
        <Marker position={posicion} icon={createCustomIcon('#007bff')}>
            <Popup>
                <div style={{ textAlign: 'center' }}>
                    <b>📍 Ubicación seleccionada</b><br />
                    {posicion.lat.toFixed(5)}, {posicion.lng.toFixed(5)}
                </div>
            </Popup>
        </Marker>
    );
}

// --- FUNCIÓN DE DISTANCIA (Haversine) ---
function calcularDistancia(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radio de la tierra en km
    const dLat = (lat2 - lat1) * (Math.PI / 180);
    const dLon = (lon2 - lon1) * (Math.PI / 180);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

function MapComponent({ user, onReserveClick }) {
    const [estaciones, setEstaciones] = useState([]);
    const [loading, setLoading] = useState(true);

    // Estados y Referencias
    const [userPos, setUserPos] = useState(null);
    const [destinoRuta, setDestinoRuta] = useState(null);
    const [geolocalizando, setGeolocalizando] = useState(false); // ✅ NUEVO ESTADO

    const mapRef = useRef(null);
    const markersRef = useRef({});

    useEffect(() => {
        fetchEstaciones();
        // ============================================
        // ✅ AUTODETECTAR UBICACIÓN AL CARGAR
        // ============================================
        autodetectarUbicacion();
    }, []);

    const fetchEstaciones = async () => {
        try {
            const response = await fetch('/api/estaciones/');
            const data = await response.json();
            setEstaciones(data);
            setLoading(false);
        } catch (error) {
            console.error('Error al cargar estaciones:', error);
            setLoading(false);
        }
    };

    // ============================================
    // ✅ FUNCIÓN DE GEOLOCALIZACIÓN AUTOMÁTICA
    // ============================================
    const autodetectarUbicacion = () => {
        if (!navigator.geolocation) {
            console.warn('Geolocalización no soportada por el navegador');
            return;
        }

        setGeolocalizando(true);

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                const nuevaPos = { lat: latitude, lng: longitude };

                setUserPos(nuevaPos);

                // Centrar el mapa en la ubicación detectada
                if (mapRef.current) {
                    mapRef.current.flyTo([latitude, longitude], 15, {
                        duration: 1.5
                    });
                }

                setGeolocalizando(false);
                console.log('✅ Ubicación detectada:', nuevaPos);
            },
            (error) => {
                console.warn('⚠️ Error al obtener ubicación:', error.message);
                setGeolocalizando(false);

                // Mensajes de error específicos
                if (error.code === error.PERMISSION_DENIED) {
                    console.log('Usuario denegó el permiso de ubicación');
                } else if (error.code === error.POSITION_UNAVAILABLE) {
                    console.log('Información de ubicación no disponible');
                } else if (error.code === error.TIMEOUT) {
                    console.log('Tiempo de espera agotado');
                }
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    };

    // ============================================
    // ✅ FUNCIÓN PARA CENTRAR EN TU MARCADOR
    // ============================================
    const centrarEnMarcador = () => {
        if (!userPos) {
            alert("⚠️ No hay ninguna ubicación marcada. Haz clic en el mapa o permite la geolocalización.");
            return;
        }

        if (mapRef.current) {
            mapRef.current.flyTo([userPos.lat, userPos.lng], 16, {
                duration: 1.5,
                easeLinearity: 0.25
            });
        }
    };

    // --- LÓGICA MODIFICADA: Buscar, Mover y TRAZAR RUTA ---
    const buscarMasCercana = () => {
        if (!userPos) {
            alert("⚠️ Primero haz clic en el mapa para marcar tu ubicación o permite la geolocalización automática.");
            return;
        }

        if (estaciones.length === 0) return;

        let masCercana = null;
        let menorDistancia = Infinity;

        estaciones.forEach(estacion => {
            const info = estacion.AddressInfo;
            if (info && info.Latitude && info.Longitude) {
                const dist = calcularDistancia(userPos.lat, userPos.lng, info.Latitude, info.Longitude);
                if (dist < menorDistancia) {
                    menorDistancia = dist;
                    masCercana = estacion;
                }
            }
        });

        if (masCercana && mapRef.current) {
            const lat = masCercana.AddressInfo.Latitude;
            const lng = masCercana.AddressInfo.Longitude;

            // 1. Establecer destino de ruta
            setDestinoRuta({ lat, lng });

            // 2. HACER ZOOM A LA ESTACIÓN (Modificado para enfoque total)
            // Usamos un zoom de 17 para que se vea bien la información
            mapRef.current.flyTo([lat, lng], 17, {
                duration: 2,
                easeLinearity: 0.25
            });

            // 3. Abrir el Popup automáticamente
            setTimeout(() => {
                const marker = markersRef.current[masCercana.ID];
                if (marker) {
                    marker.openPopup();
                }
            }, 2100); // Esperamos un poco más para que termine el desplazamiento
        }
    };

    const getIconColor = (status) => {
        if (!status) return '#9E9E9E';
        const statusLower = status.toLowerCase();
        if (statusLower.includes('available') || statusLower.includes('operational')) {
            return '#4CAF50';
        } else if (statusLower.includes('unknown')) {
            return '#9E9E9E';
        } else {
            return '#FF9800';
        }
    };

    const renderConectores = (connections) => {
        if (!connections || connections.length === 0) {
            return <p style={{ color: '#999', fontSize: '0.9rem' }}>No hay información de conectores</p>;
        }

        return (
            <div style={{ marginTop: '10px' }}>
                <h4 style={{ color: '#00c853', marginBottom: '8px', fontSize: '0.95rem' }}>🔌 Conectores:</h4>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                    {connections.map((conn, idx) => {
                        const connType = conn.ConnectionType?.Title || 'Desconocido';
                        const level = conn.Level?.Title || 'N/A';
                        const powerKW = conn.PowerKW || 'N/A';
                        const voltage = conn.Voltage || 'N/A';
                        const amps = conn.Amps || 'N/A';
                        const quantity = conn.Quantity || 1;

                        return (
                            <li key={idx} style={{
                                marginBottom: '8px', padding: '8px', background: '#f9f9f9', borderRadius: '5px', fontSize: '0.85rem'
                            }}>
                                <strong>{connType}</strong> ({quantity}x)
                                <br />
                                <small style={{ color: '#666' }}>
                                    ⚡ {powerKW} kW | 🔋 {voltage}V / {amps}A
                                    <br />
                                    📊 {level}
                                </small>
                            </li>
                        );
                    })}
                </ul>
            </div>
        );
    };

    const handleReservar = (estacion) => {
        if (!user) {
            alert('Por favor, inicia sesión para hacer una reserva');
            return;
        }
        const info = estacion.AddressInfo || {};
        const estacionFormateada = {
            id: estacion.ID,
            nombre: info?.Title || 'Estación sin nombre',
            direccion: info?.AddressLine1 || 'Dirección no disponible',
            town: info?.Town,
            state: info?.StateOrProvince,
            lat: info?.Latitude,
            lon: info?.Longitude
        };

        onReserveClick(estacionFormateada);
    };

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#00c853', fontSize: '1.2rem' }}>
                <i className="fa-solid fa-spinner fa-spin"></i>
                <span style={{ marginLeft: '0.5rem' }}>Cargando estaciones...</span>
            </div>
        );
    }

    return (
        <div style={{ position: 'relative', height: '100%', width: '100%' }}>
            <MapContainer
                center={[-25.2844487, -57.5631777]}
                zoom={13}
                style={{ height: '100%', width: '100%' }}
                zoomControl={true}
                ref={mapRef}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* --- COMPONENTE DE RUTA (Solo se activa si hay usuario y destino) --- */}
                {userPos && destinoRuta && (
                    <RutearCamino inicio={userPos} fin={destinoRuta} />
                )}

                {/* MarcadorUsuario: Pasamos la función para limpiar ruta al mover el pin */}
                <MarcadorUsuario
                    posicion={userPos}
                    setPosicion={setUserPos}
                    limpiarRuta={() => setDestinoRuta(null)}
                />

                {estaciones.map((estacion) => {
                    const info = estacion.AddressInfo;
                    if (!info || !info.Latitude || !info.Longitude) return null;
                    const status = estacion.StatusType?.Title || 'Desconocido';
                    const operator = estacion.OperatorInfo?.Title || 'Operador desconocido';
                    const usageType = estacion.UsageType?.Title || 'No especificado';
                    const numPoints = estacion.NumberOfPoints || 0;
                    let direccionCompleta = info.AddressLine1 || 'Dirección no disponible';
                    if (info.Town) direccionCompleta += `, ${info.Town}`;
                    if (info.StateOrProvince) direccionCompleta += `, ${info.StateOrProvince}`;
                    const iconColor = getIconColor(status);

                    return (
                        <Marker
                            key={estacion.ID}
                            position={[info.Latitude, info.Longitude]}
                            icon={createCustomIcon(iconColor)}
                            ref={(el) => (markersRef.current[estacion.ID] = el)}
                        >
                            <Popup maxWidth={350} minWidth={300}>
                                <div style={{ fontFamily: 'Montserrat, sans-serif' }}>
                                    <h3 style={{ margin: '0 0 10px 0', color: '#00c853', borderBottom: '2px solid #00c853', paddingBottom: '5px', fontSize: '1.1rem' }}>
                                        ⚡ {info.Title || 'Estación sin nombre'}
                                    </h3>
                                    <div style={{ marginBottom: '10px' }}>
                                        <p style={{ margin: '5px 0', fontSize: '0.9rem' }}><strong>📍 Dirección:</strong><br />{direccionCompleta}</p>
                                        <p style={{ margin: '5px 0', fontSize: '0.9rem' }}><strong>🏢 Operador:</strong> {operator}</p>
                                        <p style={{ margin: '5px 0', fontSize: '0.9rem' }}><strong>🔌 Puntos de carga:</strong> {numPoints}</p>
                                        <p style={{ margin: '5px 0', fontSize: '0.9rem' }}><strong>📊 Estado:</strong> <span style={{ color: iconColor, fontWeight: 'bold' }}>{status}</span></p>
                                        <p style={{ margin: '5px 0', fontSize: '0.9rem' }}><strong>🚪 Acceso:</strong> {usageType}</p>
                                    </div>
                                    {renderConectores(estacion.Connections)}
                                    {estacion.GeneralComments && (
                                        <p style={{ margin: '10px 0', fontSize: '0.85rem', color: '#666', fontStyle: 'italic' }}><strong>💬 Comentarios:</strong> {estacion.GeneralComments}</p>
                                    )}
                                    <button
                                        onClick={() => handleReservar(estacion)}
                                        style={{ width: '100%', padding: '12px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '5px', fontSize: '1rem', fontWeight: 'bold', cursor: 'pointer', marginTop: '15px', transition: 'background 0.3s', fontFamily: 'Montserrat, sans-serif' }}
                                        onMouseOver={(e) => e.target.style.background = '#45a049'}
                                        onMouseOut={(e) => e.target.style.background = '#4CAF50'}
                                    >
                                        📅 RESERVAR
                                    </button>
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>

            {/* ============================================ */}
            {/* ✅ BOTÓN FLOTANTE: CENTRAR EN MI UBICACIÓN */}
            {/* ============================================ */}
            <button
                onClick={centrarEnMarcador}
                disabled={!userPos}
                style={{
                    position: 'absolute',
                    bottom: '25px',
                    right: '25px',
                    zIndex: 1000,
                    background: userPos ? '#28a745' : '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    width: '56px',
                    height: '56px',
                    fontSize: '24px',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
                    cursor: userPos ? 'pointer' : 'not-allowed',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s ease',
                    opacity: userPos ? 1 : 0.6
                }}
                onMouseOver={(e) => {
                    if (userPos) e.currentTarget.style.transform = 'scale(1.1)';
                }}
                onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'scale(1)';
                }}
                title={userPos ? "Centrar en mi ubicación" : "No hay ubicación marcada"}
            >
                <i className="fa-solid fa-location-crosshairs"></i>
            </button>

            {/* --- BOTÓN FLOTANTE: BUSCAR Y TRAZAR RUTA --- */}
            <button
                onClick={buscarMasCercana}
                style={{
                    position: 'absolute',
                    bottom: '25px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    zIndex: 1000,
                    background: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50px',
                    padding: '12px 25px',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    transition: 'all 0.2s ease',
                    whiteSpace: 'nowrap'
                }}
                onMouseOver={(e) => e.currentTarget.style.transform = 'translateX(-50%) scale(1.05)'}
                onMouseOut={(e) => e.currentTarget.style.transform = 'translateX(-50%) scale(1)'}
            >
                <i className="fa-solid fa-route"></i>
                Buscar y Trazar Ruta Más Cercana
            </button>

            {/* Indicador de geolocalización en progreso */}
            {geolocalizando && (
                <div style={{
                    position: 'absolute',
                    top: '20px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    zIndex: 1000,
                    background: 'rgba(0, 123, 255, 0.9)',
                    color: 'white',
                    padding: '10px 20px',
                    borderRadius: '25px',
                    fontSize: '14px',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                }}>
                    <i className="fa-solid fa-spinner fa-spin"></i>
                    Detectando tu ubicación...
                </div>
            )}
        </div>
    );
}

export default MapComponent;