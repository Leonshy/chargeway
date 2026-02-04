import React, { useState, useEffect } from 'react';

function ReservaModal({ estacion, onClose, onSuccess }) {
    const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0]);
    const [horaInicio, setHoraInicio] = useState('');
    const [duracion, setDuracion] = useState('1');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // 🆕 Nuevos estados para conectores
    const [conectoresDisponibles, setConectoresDisponibles] = useState([]);
    const [conectorSeleccionado, setConectorSeleccionado] = useState(null);
    const [cargandoConectores, setCargandoConectores] = useState(false);
    const [errorConectores, setErrorConectores] = useState('');

    // 🔄 Obtener conectores disponibles cuando cambien fecha/hora/duración
    useEffect(() => {
        const obtenerConectoresDisponibles = async () => {
            // Solo buscar si tenemos todos los datos necesarios
            if (!estacion?.id || !fecha || !horaInicio || !duracion) {
                setConectoresDisponibles([]);
                setConectorSeleccionado(null);
                return;
            }

            setCargandoConectores(true);
            setErrorConectores('');

            try {
                const response = await fetch(
                    `/api/reservas/estacion/${estacion.id}/conectores-disponibles?` +
                    `fecha=${fecha}&hora_inicio=${horaInicio}&duracion=${duracion}`,
                    {
                        credentials: 'include'
                    }
                );

                if (response.ok) {
                    const data = await response.json();
                    setConectoresDisponibles(data.conectores || []);

                    // Auto-seleccionar el primer conector si hay disponibles
                    if (data.conectores && data.conectores.length > 0) {
                        setConectorSeleccionado(data.conectores[0]);
                    } else {
                        setConectorSeleccionado(null);
                        setErrorConectores('No hay conectores disponibles en este horario');
                    }
                } else {
                    setConectoresDisponibles([]);
                    setConectorSeleccionado(null);
                    setErrorConectores('Error al verificar disponibilidad');
                }
            } catch (err) {
                console.error('Error al obtener conectores:', err);
                setConectoresDisponibles([]);
                setConectorSeleccionado(null);
                setErrorConectores('Error de conexión');
            } finally {
                setCargandoConectores(false);
            }
        };

        obtenerConectoresDisponibles();
    }, [fecha, horaInicio, duracion, estacion?.id]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        // ✅ Validar que haya un conector seleccionado
        if (!conectorSeleccionado) {
            setError('Por favor selecciona un conector disponible');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch('/api/reservas/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    conector_id: conectorSeleccionado.id, // 🔥 CAMBIO PRINCIPAL
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
                    `Conector: ${conectorSeleccionado.nombre} (${conectorSeleccionado.tipo})\n` +
                    `Potencia: ${conectorSeleccionado.potencia_kw} kW\n` +
                    `Fecha: ${fecha}\n` +
                    `Hora: ${horaInicio}\n` +
                    `Duración: ${duracion} hora(s)\n\n` +
                    `Código de reserva: ${data.reserva?.codigo || 'N/A'}`
                );
                onSuccess();
                onClose();
            } else {
                // Manejar conflictos de disponibilidad
                if (response.status === 409 && data.conflictos) {
                    setError(`El conector ya no está disponible en este horario. Por favor selecciona otro horario.`);
                } else {
                    setError(data.error || 'Error al crear la reserva');
                }
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

                    {/* 🆕 SELECTOR DE CONECTORES */}
                    {fecha && horaInicio && duracion && (
                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '600' }}>
                                🔌 Conector:
                            </label>

                            {cargandoConectores ? (
                                <div style={{
                                    padding: '1rem',
                                    textAlign: 'center',
                                    background: '#f0f0f0',
                                    borderRadius: '8px',
                                    color: '#00c853'
                                }}>
                                    <i className="fa-solid fa-spinner fa-spin"></i>
                                    {' '}Verificando disponibilidad...
                                </div>
                            ) : conectoresDisponibles.length > 0 ? (
                                <>
                                    <select
                                        value={conectorSeleccionado?.id || ''}
                                        onChange={(e) => {
                                            const conector = conectoresDisponibles.find(
                                                c => c.id === parseInt(e.target.value)
                                            );
                                            setConectorSeleccionado(conector);
                                        }}
                                        required
                                        style={{
                                            width: '100%',
                                            padding: '0.75rem',
                                            border: '2px solid #00c853',
                                            borderRadius: '8px',
                                            fontSize: '1rem',
                                            cursor: 'pointer',
                                            background: 'white'
                                        }}
                                    >
                                        {conectoresDisponibles.map(conector => (
                                            <option key={conector.id} value={conector.id}>
                                                {conector.nombre} - {conector.tipo} ({conector.potencia_kw} kW)
                                            </option>
                                        ))}
                                    </select>
                                    <small style={{
                                        display: 'block',
                                        marginTop: '5px',
                                        color: '#00c853',
                                        fontSize: '0.85rem'
                                    }}>
                                        ✅ {conectoresDisponibles.length} conector(es) disponible(s)
                                    </small>
                                </>
                            ) : (
                                <div style={{
                                    padding: '1rem',
                                    background: '#fff3cd',
                                    border: '1px solid #ffc107',
                                    borderRadius: '8px',
                                    color: '#856404'
                                }}>
                                    ⚠️ {errorConectores || 'No hay conectores disponibles en este horario'}
                                    <br />
                                    <small style={{ fontSize: '0.85rem' }}>
                                        Intenta con otra fecha u horario
                                    </small>
                                </div>
                            )}
                        </div>
                    )}

                    {error && (
                        <div className="error-message" style={{ marginBottom: '1rem' }}>
                            {error}
                        </div>
                    )}

                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button
                            type="submit"
                            disabled={loading || !conectorSeleccionado || cargandoConectores}
                            className="login-btn"
                            style={{
                                flex: 1,
                                opacity: (!conectorSeleccionado || cargandoConectores) ? 0.5 : 1,
                                cursor: (!conectorSeleccionado || cargandoConectores) ? 'not-allowed' : 'pointer'
                            }}
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