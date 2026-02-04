import React, { useState, useEffect } from 'react';

function VehiculosEV({ user, onClose }) {
    const [misVehiculos, setMisVehiculos] = useState([]);
    const [todosLosAutos, setTodosLosAutos] = useState([]);
    const [marcasDisponibles, setMarcasDisponibles] = useState([]);
    const [modelosDisponibles, setModelosDisponibles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        auto_id: ''
    });

    useEffect(() => {
        if (user) {
            fetchMisVehiculos();
            fetchTodosLosAutos();
        }
    }, [user]);

    // Obtener todos los autos disponibles de la BD
    const fetchTodosLosAutos = async () => {
        try {
            const response = await fetch('/api/autos/', {
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                setTodosLosAutos(data);
                
                // Extraer marcas únicas
                const marcas = [...new Set(data.map(auto => auto.marca))].sort();
                setMarcasDisponibles(marcas);
            }
        } catch (error) {
            console.error('Error al cargar autos:', error);
        }
    };

    // Obtener los vehículos del usuario
    const fetchMisVehiculos = async () => {
        try {
            const response = await fetch('/api/mis-vehiculos/', {
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                setMisVehiculos(data);
            }
        } catch (error) {
            console.error('Error al cargar mis vehículos:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleMarcaChange = (marca) => {
        setFormData({ auto_id: '', marca_selected: marca });
        
        // Filtrar modelos por marca
        const modelos = todosLosAutos
            .filter(auto => auto.marca === marca)
            .sort((a, b) => a.modelo.localeCompare(b.modelo));
        
        setModelosDisponibles(modelos);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch('/api/mis-vehiculos/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ auto_id: formData.auto_id })
            });

            if (response.ok) {
                alert('Vehículo agregado exitosamente');
                setShowForm(false);
                setFormData({ auto_id: '' });
                fetchMisVehiculos();
            } else {
                const data = await response.json();
                alert(data.error || 'Error al agregar vehículo');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al agregar vehículo');
        } finally {
            setLoading(false);
        }
    };

    const eliminarVehiculo = async (vehiculoId) => {
        if (!confirm('¿Estás seguro de que deseas eliminar este vehículo?')) {
            return;
        }

        try {
            const response = await fetch(`/api/mis-vehiculos/${vehiculoId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (response.ok) {
                alert('Vehículo eliminado exitosamente');
                fetchMisVehiculos();
            } else {
                alert('Error al eliminar el vehículo');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar el vehículo');
        }
    };

    const getConectorIcon = (tipo) => {
        if (!tipo) return '🔌';
        
        const tipoLower = tipo.toLowerCase();
        if (tipoLower.includes('type 2') || tipoLower.includes('tipo 2')) return '🔌';
        if (tipoLower.includes('ccs')) return '⚡';
        if (tipoLower.includes('chademo')) return '🔋';
        if (tipoLower.includes('tesla') || tipoLower.includes('supercharger')) return '⚡';
        return '🔌';
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
                    🚗 Mis Vehículos Eléctricos
                </h2>

                {!showForm && (
                    <button
                        onClick={() => setShowForm(true)}
                        className="login-btn"
                        style={{ marginBottom: '1.5rem' }}
                    >
                        ➕ Agregar Vehículo
                    </button>
                )}

                {showForm && (
                    <div style={{
                        background: '#f9f9f9',
                        padding: '1.5rem',
                        borderRadius: '8px',
                        marginBottom: '1.5rem',
                        borderLeft: '4px solid #00c853'
                    }}>
                        <h3 style={{ marginTop: 0, color: '#333' }}>Agregar Nuevo Vehículo</h3>
                        <form onSubmit={handleSubmit}>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{
                                    display: 'block',
                                    marginBottom: '0.5rem',
                                    fontWeight: 'bold',
                                    color: '#333'
                                }}>
                                    Marca *
                                </label>
                                <select
                                    value={formData.marca_selected || ''}
                                    onChange={(e) => handleMarcaChange(e.target.value)}
                                    required
                                    style={{
                                        width: '100%',
                                        padding: '0.75rem',
                                        border: '2px solid #e0e0e0',
                                        borderRadius: '8px',
                                        fontSize: '1rem',
                                        fontFamily: 'Montserrat, sans-serif'
                                    }}
                                >
                                    <option value="">Selecciona una marca</option>
                                    {marcasDisponibles.map(marca => (
                                        <option key={marca} value={marca}>{marca}</option>
                                    ))}
                                </select>
                            </div>

                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{
                                    display: 'block',
                                    marginBottom: '0.5rem',
                                    fontWeight: 'bold',
                                    color: '#333'
                                }}>
                                    Modelo *
                                </label>
                                <select
                                    value={formData.auto_id}
                                    onChange={(e) => setFormData({ ...formData, auto_id: e.target.value })}
                                    required
                                    disabled={!formData.marca_selected}
                                    style={{
                                        width: '100%',
                                        padding: '0.75rem',
                                        border: '2px solid #e0e0e0',
                                        borderRadius: '8px',
                                        fontSize: '1rem',
                                        fontFamily: 'Montserrat, sans-serif',
                                        background: !formData.marca_selected ? '#f5f5f5' : 'white'
                                    }}
                                >
                                    <option value="">Selecciona un modelo</option>
                                    {modelosDisponibles.map(auto => (
                                        <option key={auto.id} value={auto.id}>
                                            {auto.modelo} ({auto.año}) - {auto.autonomia_km}km autonomía
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {formData.auto_id && (
                                <div style={{
                                    background: '#e8f5e9',
                                    padding: '1rem',
                                    borderRadius: '8px',
                                    marginBottom: '1rem'
                                }}>
                                    {(() => {
                                        const autoSeleccionado = todosLosAutos.find(a => a.id === parseInt(formData.auto_id));
                                        return autoSeleccionado ? (
                                            <>
                                                <p style={{ margin: '5px 0', fontSize: '0.9rem' }}>
                                                    <strong>📊 Especificaciones:</strong>
                                                </p>
                                                <p style={{ margin: '5px 0', fontSize: '0.85rem' }}>
                                                    🔋 Batería: {autoSeleccionado.bateria_kwh} kWh
                                                </p>
                                                <p style={{ margin: '5px 0', fontSize: '0.85rem' }}>
                                                    📏 Autonomía: {autoSeleccionado.autonomia_km} km
                                                </p>
                                                <p style={{ margin: '5px 0', fontSize: '0.85rem' }}>
                                                    ⚡ Potencia: {autoSeleccionado.potencia_hp} HP
                                                </p>
                                                <p style={{ margin: '5px 0', fontSize: '0.85rem' }}>
                                                    📊 Consumo: {autoSeleccionado.consumo_est_kwh_100km} kWh/100km
                                                </p>
                                                <p style={{ margin: '5px 0', fontSize: '0.85rem' }}>
                                                    🔌 Puerto: {autoSeleccionado.puerto_de_carga}
                                                </p>
                                            </>
                                        ) : null;
                                    })()}
                                </div>
                            )}

                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <button
                                    type="submit"
                                    className="login-btn"
                                    disabled={loading || !formData.auto_id}
                                    style={{ flex: 1 }}
                                >
                                    {loading ? 'Guardando...' : '💾 Guardar'}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowForm(false);
                                        setFormData({ auto_id: '' });
                                        setModelosDisponibles([]);
                                    }}
                                    style={{
                                        flex: 1,
                                        padding: '0.75rem',
                                        background: '#666',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '8px',
                                        fontSize: '1rem',
                                        fontWeight: '600',
                                        cursor: 'pointer',
                                        fontFamily: 'Montserrat, sans-serif'
                                    }}
                                >
                                    Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                )}

                {loading && !showForm ? (
                    <div style={{ textAlign: 'center', padding: '2rem', color: '#00c853' }}>
                        <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem' }}></i>
                        <p style={{ marginTop: '1rem' }}>Cargando vehículos...</p>
                    </div>
                ) : misVehiculos.length === 0 && !showForm ? (
                    <div style={{
                        textAlign: 'center',
                        padding: '3rem',
                        color: '#999',
                        background: '#f9f9f9',
                        borderRadius: '8px'
                    }}>
                        <i className="fa-solid fa-car" style={{ fontSize: '3rem', marginBottom: '1rem' }}></i>
                        <p style={{ fontSize: '1.1rem' }}>No tienes vehículos registrados</p>
                        <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
                            Agrega tu vehículo eléctrico para una mejor experiencia
                        </p>
                    </div>
                ) : !showForm && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {misVehiculos.map((vehiculo) => (
                            <div
                                key={vehiculo.id}
                                style={{
                                    background: '#f9f9f9',
                                    padding: '1.2rem',
                                    borderRadius: '8px',
                                    borderLeft: '4px solid #00c853',
                                    transition: 'transform 0.2s',
                                }}
                                onMouseOver={(e) => e.currentTarget.style.transform = 'translateX(5px)'}
                                onMouseOut={(e) => e.currentTarget.style.transform = 'translateX(0)'}
                            >
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'flex-start',
                                    marginBottom: '0.8rem'
                                }}>
                                    <h3 style={{
                                        margin: 0,
                                        color: '#333',
                                        fontSize: '1.2rem'
                                    }}>
                                        🚗 {vehiculo.marca} {vehiculo.modelo}
                                    </h3>
                                    <span style={{
                                        background: '#00c853',
                                        color: 'white',
                                        padding: '0.3rem 0.8rem',
                                        borderRadius: '20px',
                                        fontSize: '0.85rem',
                                        fontWeight: 'bold'
                                    }}>
                                        {vehiculo.año}
                                    </span>
                                </div>

                                <div style={{ marginBottom: '0.5rem' }}>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>🔋 Batería:</strong> {vehiculo.bateria_kwh} kWh
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>📏 Autonomía:</strong> {vehiculo.autonomia_km} km
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>⚡ Potencia:</strong> {vehiculo.potencia_hp} HP
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>{getConectorIcon(vehiculo.puerto_de_carga)} Puerto de Carga:</strong> {vehiculo.puerto_de_carga}
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>📊 Consumo:</strong> {vehiculo.consumo_est_kwh_100km} kWh/100km
                                    </p>
                                    <p style={{ margin: '5px 0', fontSize: '0.9rem', color: '#666' }}>
                                        <strong>🚙 Tipo:</strong> {vehiculo.tipo}
                                    </p>
                                </div>

                                <div style={{ marginTop: '1rem' }}>
                                    <button
                                        onClick={() => eliminarVehiculo(vehiculo.id)}
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
                                        🗑️ Eliminar
                                    </button>
                                </div>
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

export default VehiculosEV;