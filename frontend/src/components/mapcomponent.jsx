import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

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

// --- NUEVO COMPONENTE: Maneja el clic del usuario ---
function MarcadorUsuario() {
    const [posicion, setPosicion] = useState(null);

    // useMapEvents permite acceder a los eventos del mapa
    useMapEvents({
        click(e) {
            setPosicion(e.latlng); // Guardamos la latitud y longitud del clic
        },
    });

    // Si no hay posición (aún no hizo clic), no renderizamos nada
    if (posicion === null) return null;

    // Usamos un color AZUL (#007bff) para diferenciarlo de las estaciones
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

function MapComponent({ user, onReserveClick }) {
    const [estaciones, setEstaciones] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchEstaciones();
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
                                marginBottom: '8px',
                                padding: '8px',
                                background: '#f9f9f9',
                                borderRadius: '5px',
                                fontSize: '0.85rem'
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
        onReserveClick({
            id: estacion.ID,
            nombre: info.Title || 'Estación sin nombre',
            direccion: info.AddressLine1 || 'Dirección no disponible',
            town: info.Town || '',
            state: info.StateOrProvince || ''
        });
    };

    if (loading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
                color: '#00c853',
                fontSize: '1.2rem'
            }}>
                <i className="fa-solid fa-spinner fa-spin"></i>
                <span style={{ marginLeft: '0.5rem' }}>Cargando estaciones...</span>
            </div>
        );
    }

    return (
        <MapContainer
            center={[-25.2844487, -57.5631777]}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
            zoomControl={true}
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MarcadorUsuario />

            {estaciones.map((estacion) => {
                const info = estacion.AddressInfo;
                if (!info || !info.Latitude || !info.Longitude) return null;

                const status = estacion.StatusType?.Title || 'Desconocido';
                const operator = estacion.OperatorInfo?.Title || 'Operador desconocido';
                const usageType = estacion.UsageType?.Title || 'No especificado';
                const numPoints = estacion.NumberOfPoints || 0;

                // Construir dirección completa
                let direccionCompleta = info.AddressLine1 || 'Dirección no disponible';
                if (info.Town) direccionCompleta += `, ${info.Town}`;
                if (info.StateOrProvince) direccionCompleta += `, ${info.StateOrProvince}`;

                const iconColor = getIconColor(status);

                return (
                    <Marker
                        key={estacion.ID}
                        position={[info.Latitude, info.Longitude]}
                        icon={createCustomIcon(iconColor)}
                    >
                        <Popup maxWidth={350} minWidth={300}>
                            <div style={{ fontFamily: 'Montserrat, sans-serif' }}>
                                <h3 style={{
                                    margin: '0 0 10px 0',
                                    color: '#00c853',
                                    borderBottom: '2px solid #00c853',
                                    paddingBottom: '5px',
                                    fontSize: '1.1rem'
                                }}>
                                    ⚡ {info.Title || 'Estación sin nombre'}
                                </h3>

                                <div style={{ marginBottom: '10px' }}>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem' }}>
                                        <strong>📍 Dirección:</strong><br />
                                        {direccionCompleta}
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem' }}>
                                        <strong>🏢 Operador:</strong> {operator}
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem' }}>
                                        <strong>🔌 Puntos de carga:</strong> {numPoints}
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem' }}>
                                        <strong>📊 Estado:</strong>{' '}
                                        <span style={{ color: iconColor, fontWeight: 'bold' }}>
                                            {status}
                                        </span>
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem' }}>
                                        <strong>🚪 Acceso:</strong> {usageType}
                                    </p>
                                </div>

                                {renderConectores(estacion.Connections)}

                                {estacion.GeneralComments && (
                                    <p style={{
                                        margin: '10px 0',
                                        fontSize: '0.85rem',
                                        color: '#666',
                                        fontStyle: 'italic'
                                    }}>
                                        <strong>💬 Comentarios:</strong> {estacion.GeneralComments}
                                    </p>
                                )}

                                <button
                                    onClick={() => handleReservar(estacion)}
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        background: '#4CAF50',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '5px',
                                        fontSize: '1rem',
                                        fontWeight: 'bold',
                                        cursor: 'pointer',
                                        marginTop: '15px',
                                        transition: 'background 0.3s',
                                        fontFamily: 'Montserrat, sans-serif'
                                    }}
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
    );
}

export default MapComponent;