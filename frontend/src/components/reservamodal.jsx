
import React, { useState } from 'react';

function ReservaModal({ estacion, onClose, onSuccess }) {
    const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0]);
    const [horaInicio, setHoraInicio] = useState('');
    const [duracion, setDuracion] = useState('1');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch('/api/reservas/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    estacion_id: estacion.id,
                    estacion_nombre: estacion.nombre,
                    estacion_direccion: `${estacion.direccion}${estacion.town ? ', ' + estacion.town : ''}${estacion.state ? ', ' + estacion.state : ''}`,
                    fecha: fecha,
                    hora_inicio: horaInicio,
                    duracion: parseFloat(duracion)
                })
            });

            const data = await response.json();

            if (response.ok) {
                alert('¡Reserva creada exitosamente!\n\n' +
                    'Detalles:\n' +
                    `Estación: ${estacion.nombre}\n` +
                    `Fecha: ${fecha}\n` +
                    `Hora: ${horaInicio}\n` +
                    `Duración: ${duracion} hora(s)`
                );
                onSuccess();
                onClose();
            } else {
                setError(data.error || 'Error al crear la reserva');
            }
        } catch (err) {
            console.error('Error:', err);
            setError('Error de conexión. Por favor, intenta de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-overlay" onClick={onClose}>
            <div className="login-box" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '500px' }}>
                <button className="close-btn" onClick={onClose}>×</button>

                <h2 style={{ color: '#00c853' }}>📅 Reservar Estación</h2>

                <div style={{ marginBottom: '1rem', padding: '1rem', background: '#f9f9f9', borderRadius: '8px' }}>
                    <p style={{ margin: '5px 0' }}><strong>🏢 Estación:</strong> {estacion.nombre}</p>
                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                        <strong>📍 Dirección:</strong> {estacion.direccion}
                        {estacion.town && `, ${estacion.town}`}
                        {estacion.state && `, ${estacion.state}`}
                    </p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>
                            📅 Fecha:
                        </label>
                        <input
                            type="date"
                            value={fecha}
                            onChange={(e) => setFecha(e.target.value)}
                            min={new Date().toISOString().split('T')[0]}
                            required
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '2px solid #e0e0e0',
                                borderRadius: '8px',
                                fontSize: '1rem'
                            }}
                        />
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>
                            🕐 Hora de inicio:
                        </label>
                        <input
                            type="time"
                            value={horaInicio}
                            onChange={(e) => setHoraInicio(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '2px solid #e0e0e0',
                                borderRadius: '8px',
                                fontSize: '1rem'
                            }}
                        />
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>
                            ⏱️ Duración:
                        </label>
                        <select
                            value={duracion}
                            onChange={(e) => setDuracion(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '2px solid #e0e0e0',
                                borderRadius: '8px',
                                fontSize: '1rem',
                                cursor: 'pointer'
                            }}
                        >
                            <option value="0.5">30 minutos</option>
                            <option value="1">1 hora</option>
                            <option value="2">2 horas</option>
                            <option value="3">3 horas</option>
                            <option value="4">4 horas</option>
                            <option value="6">6 horas</option>
                            <option value="8">8 horas</option>
                        </select>
                    </div>

                    {error && (
                        <div className="error-message" style={{ marginBottom: '1rem' }}>
                            {error}
                        </div>
                    )}

                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button
                            type="submit"
                            disabled={loading}
                            className="login-btn"
                            style={{ flex: 1 }}
                        >
                            {loading ? '⏳ Reservando...' : '✅ Confirmar Reserva'}
                        </button>
                        <button
                            type="button"
                            onClick={onClose}
                            disabled={loading}
                            style={{
                                flex: 1,
                                padding: '0.75rem',
                                background: '#f44336',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                fontSize: '1rem',
                                fontWeight: '600',
                                cursor: 'pointer',
                                fontFamily: 'Montserrat, sans-serif'
                            }}
                        >
                            ❌ Cancelar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default ReservaModal;