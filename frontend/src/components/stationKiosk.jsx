import React, { useState, useEffect } from "react";
import "./StationKiosk.css";

function StationKiosk({ onClose }) { // 🆕 Ahora recibe onClose como prop
    const [codigo, setCodigo] = useState("");
    const [estado, setEstado] = useState("idle");
    const [reserva, setReserva] = useState(null);
    const [estacion, setEstacion] = useState(null);
    const [conectores, setConectores] = useState([]);
    const [conectorSeleccionado, setConectorSeleccionado] = useState(null);
    const [error, setError] = useState("");
    const [tiempoRestante, setTiempoRestante] = useState(null);
    const [resumen, setResumen] = useState(null);

    // Polling para actualizar tiempo restante
    useEffect(() => {
        let interval;

        if (estado === "en_progreso" && reserva) {
            interval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/kiosk/estado/${reserva.codigo}`);
                    if (response.ok) {
                        const data = await response.json();
                        setTiempoRestante(data.tiempo_restante);

                        if (data.reserva.estado === "completada") {
                            setEstado("completada");
                        }
                    }
                } catch (err) {
                    console.error("Error actualizando estado:", err);
                }
            }, 10000);
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [estado, reserva]);

    const handleVerificarCodigo = async (e) => {
        e.preventDefault();

        if (!codigo.trim()) {
            setError("Ingrese un código de reserva");
            return;
        }

        setEstado("verificando");
        setError("");

        try {
            const response = await fetch("/api/kiosk/verificar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ codigo: codigo.toUpperCase() })
            });

            const data = await response.json();

            if (response.ok && data.valid) {
                setReserva(data.reserva);
                setEstacion(data.estacion);
                setConectores(data.conectores_disponibles || []);

                if (data.reserva.estado === "en_progreso") {
                    setEstado("en_progreso");
                } else {
                    setEstado("activa");
                }
            } else {
                setError(data.error || "Código inválido");
                setEstado("error");
                setTimeout(() => {
                    setEstado("idle");
                    setCodigo("");
                }, 3000);
            }
        } catch (err) {
            console.error("Error:", err);
            setError("Error de conexión. Intente nuevamente.");
            setEstado("error");
            setTimeout(() => setEstado("idle"), 3000);
        }
    };

    const handleIniciarCarga = async () => {
        try {
            const response = await fetch("/api/kiosk/iniciar-carga", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    codigo: reserva.codigo,
                    conector_id: conectorSeleccionado
                })
            });

            const data = await response.json();

            if (response.ok) {
                setReserva(data.reserva);
                setEstado("en_progreso");
            } else {
                setError(data.error || "Error al iniciar carga");
            }
        } catch (err) {
            setError("Error de conexión");
        }
    };

    const handleFinalizarCarga = async () => {
        if (!confirm("¿Confirma que desea finalizar la carga?")) return;

        try {
            const response = await fetch("/api/kiosk/finalizar-carga", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ codigo: reserva.codigo })
            });

            const data = await response.json();

            if (response.ok) {
                setResumen(data.resumen);
                setEstado("completada");

                setTimeout(() => {
                    handleReset();
                }, 10000);
            } else {
                setError(data.error || "Error al finalizar carga");
            }
        } catch (err) {
            setError("Error de conexión");
        }
    };

    const handleReset = () => {
        setCodigo("");
        setEstado("idle");
        setReserva(null);
        setEstacion(null);
        setConectores([]);
        setConectorSeleccionado(null);
        setError("");
        setTiempoRestante(null);
        setResumen(null);
    };

    const calcularHoraFin = () => {
        if (!reserva) return "";

        const [horas, minutos] = reserva.hora_inicio.split(":");
        const inicio = new Date();
        inicio.setHours(parseInt(horas), parseInt(minutos));

        const fin = new Date(inicio.getTime() + reserva.duracion_horas * 60 * 60 * 1000);

        return fin.toLocaleTimeString('es-PY', { hour: '2-digit', minute: '2-digit' });
    };

    // ============================================
    // 🎨 RENDERS
    // ============================================
    const renderPantallaInicial = () => (
        <div className="kiosk-screen inicial">
            <div className="kiosk-header">
                <h1>⚡ Estación de Carga</h1>
                <p>Bienvenido a ChargeWay</p>
            </div>

            <div className="kiosk-content">
                <div className="welcome-message">
                    <div className="icon-large">🔌</div>
                    <h2>Ingrese su código de reserva</h2>
                    <p>Encontrará el código en su email de confirmación</p>
                </div>

                <form onSubmit={handleVerificarCodigo} className="codigo-form">
                    <input
                        type="text"
                        value={codigo}
                        onChange={(e) => setCodigo(e.target.value.toUpperCase())}
                        placeholder="Ej: ABC12345"
                        maxLength={20}
                        className="codigo-input"
                        autoFocus
                    />

                    <button type="submit" className="btn-primary btn-large">
                        Verificar Reserva
                    </button>
                </form>

                {error && (
                    <div className="kiosk-error">
                        ❌ {error}
                    </div>
                )}
            </div>

            <div className="kiosk-footer">
                <p>¿Necesita ayuda? Contacte al personal de la estación</p>
            </div>
        </div>
    );

    const renderVerificando = () => (
        <div className="kiosk-screen verificando">
            <div className="spinner-large"></div>
            <h2>Verificando código...</h2>
        </div>
    );

    const renderReservaActiva = () => (
        <div className="kiosk-screen activa">
            <div className="kiosk-header success">
                <div className="icon-success">✅</div>
                <h1>Reserva Confirmada</h1>
            </div>

            <div className="kiosk-content">
                <div className="reserva-info">
                    <div className="info-card">
                        <h3>👤 Usuario</h3>
                        <p className="info-value">{reserva?.usuario?.username || "Usuario"}</p>
                    </div>

                    <div className="info-card">
                        <h3>📍 Estación</h3>
                        <p className="info-value">{reserva?.estacion_nombre}</p>
                        <p className="info-detail">{reserva?.estacion_direccion}</p>
                    </div>

                    <div className="info-card">
                        <h3>⏰ Horario Reservado</h3>
                        <p className="info-value">
                            {reserva?.hora_inicio} - {calcularHoraFin()}
                        </p>
                        <p className="info-detail">Duración: {reserva?.duracion_horas}h</p>
                    </div>

                    <div className="info-card">
                        <h3>🔌 Código de Reserva</h3>
                        <p className="info-value codigo-grande">{reserva?.codigo}</p>
                    </div>
                </div>

                {conectores.length > 0 && (
                    <div className="conectores-section">
                        <h3>Seleccione un conector (opcional)</h3>
                        <div className="conectores-grid">
                            {conectores.map((conector) => (
                                <button
                                    key={conector.id}
                                    className={`conector-card ${conectorSeleccionado === conector.id ? "selected" : ""
                                        }`}
                                    onClick={() => setConectorSeleccionado(conector.id)}
                                >
                                    <div className="conector-nombre">{conector.nombre}</div>
                                    <div className="conector-tipo">{conector.tipo}</div>
                                    <div className="conector-potencia">{conector.potencia_kw} kW</div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                <div className="actions">
                    <button onClick={handleIniciarCarga} className="btn-success btn-xlarge">
                        🚀 Iniciar Carga
                    </button>
                    <button onClick={handleReset} className="btn-secondary">
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    );

    const renderEnProgreso = () => (
        <div className="kiosk-screen en-progreso">
            <div className="kiosk-header progress">
                <div className="icon-charging">🔋</div>
                <h1>Carga en Progreso</h1>
            </div>

            <div className="kiosk-content">
                <div className="charging-status">
                    {tiempoRestante && (
                        <>
                            <div className="tiempo-restante">
                                <h2>
                                    {tiempoRestante.horas}h {tiempoRestante.minutos}m
                                </h2>
                                <p>Tiempo restante estimado</p>
                            </div>

                            <div className="progress-bar-container">
                                <div
                                    className="progress-bar-fill"
                                    style={{ width: `${tiempoRestante.porcentaje_completado}%` }}
                                ></div>
                            </div>

                            <div className="porcentaje">
                                {tiempoRestante.porcentaje_completado}% completado
                            </div>
                        </>
                    )}

                    <div className="info-grid">
                        <div className="info-item">
                            <span className="label">Usuario:</span>
                            <span className="value">{reserva?.usuario?.username}</span>
                        </div>
                        <div className="info-item">
                            <span className="label">Inicio:</span>
                            <span className="value">
                                {reserva?.hora_inicio_real
                                    ? new Date(reserva.hora_inicio_real).toLocaleTimeString('es-PY')
                                    : '-'}
                            </span>
                        </div>
                        <div className="info-item">
                            <span className="label">Duración programada:</span>
                            <span className="value">{reserva?.duracion_horas}h</span>
                        </div>
                        {reserva?.conector_id && (
                            <div className="info-item">
                                <span className="label">Conector:</span>
                                <span className="value">#{reserva.conector_id}</span>
                            </div>
                        )}
                    </div>
                </div>

                <div className="actions">
                    <button onClick={handleFinalizarCarga} className="btn-danger btn-xlarge">
                        🏁 Finalizar Carga
                    </button>
                </div>
            </div>

            <div className="kiosk-footer">
                <p>⚠️ No desconecte el vehículo hasta finalizar la carga</p>
            </div>
        </div>
    );

    const renderCompletada = () => (
        <div className="kiosk-screen completada">
            <div className="kiosk-header success">
                <div className="icon-success">🎉</div>
                <h1>Carga Completada</h1>
            </div>

            <div className="kiosk-content">
                {resumen && (
                    <div className="resumen-container">
                        <h2>Resumen de la Sesión</h2>

                        <div className="resumen-grid">
                            <div className="resumen-item">
                                <span className="label">Inicio Real:</span>
                                <span className="value">
                                    {new Date(resumen.resumen.hora_inicio_real).toLocaleTimeString('es-PY')}
                                </span>
                            </div>
                            <div className="resumen-item">
                                <span className="label">Fin:</span>
                                <span className="value">
                                    {new Date(resumen.resumen.hora_fin_real).toLocaleTimeString('es-PY')}
                                </span>
                            </div>
                            <div className="resumen-item">
                                <span className="label">Duración Real:</span>
                                <span className="value highlight">
                                    {resumen.resumen.duracion_real_horas}h
                                </span>
                            </div>
                            <div className="resumen-item">
                                <span className="label">Duración Programada:</span>
                                <span className="value">
                                    {resumen.resumen.duracion_programada_horas}h
                                </span>
                            </div>
                        </div>

                        <div className="mensaje-final">
                            <p>✅ Puede desconectar su vehículo con seguridad</p>
                            <p>Gracias por usar ChargeWay</p>
                        </div>
                    </div>
                )}

                <div className="actions">
                    <button onClick={handleReset} className="btn-primary btn-xlarge">
                        ✨ Nueva Reserva
                    </button>
                </div>
            </div>

            <div className="auto-reset">
                Reiniciando en 10 segundos...
            </div>
        </div>
    );

    // 🆕 Render principal como OVERLAY (igual que tus otros modales)
    return (
        <div className="kiosk-overlay" onClick={onClose}>
            <div className="kiosk-container" onClick={(e) => e.stopPropagation()}>
                {/* Botón de cerrar */}
                <button className="btn-exit-kiosk" onClick={onClose}>
                    ✕ Cerrar
                </button>

                {estado === "idle" && renderPantallaInicial()}
                {estado === "verificando" && renderVerificando()}
                {estado === "activa" && renderReservaActiva()}
                {estado === "en_progreso" && renderEnProgreso()}
                {estado === "completada" && renderCompletada()}
                {estado === "error" && renderPantallaInicial()}
            </div>
        </div>
    );
}

export default StationKiosk;