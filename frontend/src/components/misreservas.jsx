import React, { useState, useEffect } from 'react';

function MisReservas({ user, onClose }) {
    const [reservas, setReservas] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user) {
            fetchReservas();
        }
    }, [user]);

    const fetchReservas = async () => {
        try {
            const response = await fetch('/api/reservas/', {
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                setReservas(data);
            }
        } catch (error) {
            console.error('Error al cargar reservas:', error);
        } finally {
            setLoading(false);
        }
    };

    const cancelarReserva = async (reservaId) => {
        if (!confirm('¿Estás seguro de que deseas cancelar esta reserva?')) {
            return;
        }

        try {
            const response = await fetch(`/api/reservas/${reservaId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (response.ok) {
                alert('Reserva cancelada exitosamente');
                fetchReservas(); // Recargar la lista
            } else {
                alert('Error al cancelar la reserva');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al cancelar la reserva');
        }
    };

    const getEstadoColor = (estado) => {
        switch (estado.toLowerCase()) {
            case 'activa':
                return '#4CAF50';
            case 'completada':
                return '#2196F3';
            case 'cancelada':
                return '#f44336';
            default:
                return '#9E9E9E';
        }
    };

    const getEstadoEmoji = (estado) => {
        switch (estado.toLowerCase()) {
            case 'activa':
                return '✅';
            case 'completada':
                return '✔️';
            case 'cancelada':
                return '❌';
            default:
                return '❓';
        }
    };

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
                    📋 Mis Reservas
                </h2>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '2rem', color: '#00c853' }}>
                        <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem' }}></i>
                        <p style={{ marginTop: '1rem' }}>Cargando reservas...</p>
                    </div>
                ) : reservas.length === 0 ? (
                    <div style={{
                        textAlign: 'center',
                        padding: '3rem',
                        color: '#999',
                        background: '#f9f9f9',
                        borderRadius: '8px'
                    }}>
                        <i className="fa-solid fa-calendar-xmark" style={{ fontSize: '3rem', marginBottom: '1rem' }}></i>
                        <p style={{ fontSize: '1.1rem' }}>No tienes reservas activas</p>
                        <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
                            Haz clic en cualquier estación del mapa para crear una reserva
                        </p>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {reservas.map((reserva) => (
                            <div
                                key={reserva.id}
                                style={{
                                    background: '#f9f9f9',
                                    padding: '1.2rem',
                                    borderRadius: '8px',
                                    borderLeft: `4px solid ${getEstadoColor(reserva.estado)}`,
                                    transition: 'transform 0.2s',
                                }}
                                onMouseOver={(e) => e.currentTarget.style.transform = 'translateX(5px)'}
                                onMouseOut={(e) => e.currentTarget.style.transform = 'translateX(0)'}
                            >
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'flex-start',
                                    marginBottom: '0.8rem',
                                    flexWrap: 'wrap',
                                    gap: '0.5rem'
                                }}>
                                    <h3 style={{
                                        margin: 0,
                                        color: '#333',
                                        fontSize: '1.1rem',
                                        flex: '1'
                                    }}>
                                        ⚡ {reserva.estacion_nombre}
                                    </h3>
                                    <span style={{
                                        background: getEstadoColor(reserva.estado),
                                        color: 'white',
                                        padding: '0.3rem 0.8rem',
                                        borderRadius: '20px',
                                        fontSize: '0.85rem',
                                        fontWeight: 'bold',
                                        whiteSpace: 'nowrap'
                                    }}>
                                        {getEstadoEmoji(reserva.estado)} {reserva.estado.toUpperCase()}
                                    </span>
                                </div>

                                <div style={{ marginBottom: '0.5rem' }}>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>📍 Dirección:</strong> {reserva.estacion_direccion}
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>📅 Fecha:</strong> {reserva.fecha}
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>🕐 Hora:</strong> {reserva.hora_inicio}
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>⏱️ Duración:</strong> {reserva.duracion_horas} hora(s)
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.85rem', color: '#999' }}>
                                        <strong>Creada el:</strong> {reserva.created_at}
                                    </p>
                                </div>

                                {reserva.estado.toLowerCase() === 'activa' && (
                                    <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                                        <button
                                            onClick={() => cancelarReserva(reserva.id)}
                                            style={{
                                                padding: '0.6rem 1.2rem',
                                                background: '#f44336',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '5px',
                                                cursor: 'pointer',
                                                fontSize: '0.9rem',
                                                fontWeight: '600',
                                                transition: 'background 0.3s',
                                                fontFamily: 'Montserrat, sans-serif'
                                            }}
                                            onMouseOver={(e) => e.target.style.background = '#d32f2f'}
                                            onMouseOut={(e) => e.target.style.background = '#f44336'}
                                        >
                                            ❌ Cancelar Reserva
                                        </button>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

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

export default MisReservas;