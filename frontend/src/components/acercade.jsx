import React from 'react';

function AcercaDe({ onClose }) {
    return (
        <div className="login-overlay" onClick={onClose}>
            <div
                className="login-box"
                onClick={(e) => e.stopPropagation()}
                style={{
                    maxWidth: '700px',
                    maxHeight: '90vh',
                    overflow: 'auto',
                    width: '95%'
                }}
            >
                <button className="close-btn" onClick={onClose}>×</button>

                <h2 style={{ color: '#00c853', marginBottom: '1.5rem' }}>
                    ℹ️ Acerca de ChargeWay
                </h2>

                <div style={{
                    background: '#f9f9f9',
                    padding: '1.5rem',
                    borderRadius: '8px',
                    borderLeft: '4px solid #00c853',
                    marginBottom: '1.5rem'
                }}>
                    <p style={{ fontSize: '1rem', color: '#333', lineHeight: '1.6' }}>
                        <strong>ChargeWay</strong> es una plataforma pensada para facilitar
                        la experiencia de los usuarios de vehículos eléctricos, permitiendo
                        localizar puntos de carga, gestionar reservas y administrar vehículos
                        desde un único lugar.
                    </p>

                    <p style={{ fontSize: '0.95rem', color: '#555', marginTop: '1rem' }}>
                        El objetivo principal del proyecto es impulsar la movilidad eléctrica
                        y mejorar la accesibilidad a la infraestructura de carga, brindando
                        información clara y herramientas prácticas.
                    </p>
                </div>

                <div style={{
                    background: '#ffffff',
                    padding: '1.5rem',
                    borderRadius: '8px',
                    border: '1px solid #e0e0e0',
                    marginBottom: '1.5rem'
                }}>
                    <h3 style={{ marginTop: 0, color: '#333' }}>⚙️ Tecnologías utilizadas</h3>

                    <ul style={{ paddingLeft: '1.2rem', color: '#555', lineHeight: '1.6' }}>
                        <li>⚛️ React para la interfaz de usuario</li>
                        <li>🐍 Backend con Python / Flask</li>
                        <li>🗺️ Mapas interactivos con Leaflet</li>
                        <li>🔌 APIs de estaciones de carga</li>
                        <li>🔐 Autenticación basada en sesión</li>
                    </ul>
                </div>

                <div style={{
                    background: '#e8f5e9',
                    padding: '1.2rem',
                    borderRadius: '8px'
                }}>
                    <p style={{ margin: 0, fontSize: '0.9rem', color: '#2e7d32' }}>
                        🚀 Proyecto en desarrollo — nuevas funciones serán incorporadas
                        progresivamente para mejorar la experiencia del usuario.
                    </p>
                </div>

                <button
                    onClick={onClose}
                    className="login-btn"
                    style={{
                        marginTop: '1.5rem',
                        background: '#666'
                    }}
                >
                    Cerrar
                </button>
            </div>
        </div>
    );
}

export default AcercaDe;
