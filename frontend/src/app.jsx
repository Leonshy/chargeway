import React, { useState, useEffect } from "react";
import Header from "./components/header";
import Login from "./components/Login"; // Asegúrate que el nombre del archivo coincida (mayúscula/minúscula)
import MapComponent from "./components/mapcomponent";
import ReservaModal from "./components/ReservaModal";
import MisReservas from "./components/MisReservas";
import AdminPanel from "./adminPanel"; // Importamos el Admin
import VehiculosEV from "./components/vehiculo";   // Importamos la gestión de Vehículos

// --- CONFIGURACIÓN: CORREO DE ADMINISTRADOR ---
const ADMIN_EMAIL = "admin@chargeway.com"; // <--- CAMBIA ESTO POR TU EMAIL REAL

function App() {
  // --- ESTADOS ---
  const [showLogin, setShowLogin] = useState(false);
  const [showReservas, setShowReservas] = useState(false);
  const [showVehiculos, setShowVehiculos] = useState(false); // Estado para modal vehículos
  const [showReservaModal, setShowReservaModal] = useState(false);
  const [estacionSeleccionada, setEstacionSeleccionada] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Estado para controlar si vemos el Mapa o el Admin
  const [vistaActual, setVistaActual] = useState('mapa'); 

  // --- EFECTOS ---
  useEffect(() => {
    // Cargar usuario del almacenamiento local al iniciar
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  // --- MANEJADORES ---
  const handleLoginSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    setShowLogin(false);
    
    // Seguridad: Si no es admin, forzar vista mapa
    if (userData.email !== ADMIN_EMAIL) {
      setVistaActual('mapa');
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    setShowReservas(false);
    setShowVehiculos(false);
    setVistaActual('mapa'); // Al salir, volver siempre al mapa
  };

  const handleReservarClick = (estacion) => {
    if (!user) {
      setShowLogin(true);
    } else {
      setEstacionSeleccionada(estacion);
      setShowReservaModal(true);
    }
  };

  // Verificar si es administrador
  const isAdmin = user && user.email === ADMIN_EMAIL;

  if (loading) {
    return <div style={{ color: 'green', padding: '20px', textAlign: 'center' }}>Cargando Chargeway...</div>;
  }

  return (
    <div style={{ height: '100vh', overflow: 'hidden', position: 'relative' }}>
      
      {/* --- BOTÓN FLOTANTE ADMIN (Solo visible si es Admin) --- */}
      {isAdmin && (
          <button 
            onClick={() => setVistaActual(vistaActual === 'mapa' ? 'admin' : 'mapa')}
            style={{
                position: 'fixed', bottom: 10, left: 10, zIndex: 9999,
                background: '#dc3545', color: 'white', border: 'none', padding: '8px 15px',
                borderRadius: '5px', opacity: 0.9, cursor: 'pointer', fontSize: '12px',
                boxShadow: '0 2px 5px rgba(0,0,0,0.3)', fontWeight: 'bold'
            }}
          >
            {vistaActual === 'mapa' ? '⚙️ Panel Admin' : '🗺️ Volver al Mapa'}
          </button>
      )}

      {/* --- RENDERIZADO CONDICIONAL: ADMIN vs USUARIO --- */}
      {isAdmin && vistaActual === 'admin' ? (
        // VISTA 1: PANEL DE ADMINISTRACIÓN
        <AdminPanel />
      ) : (
        // VISTA 2: APLICACIÓN PRINCIPAL (Mapa, Header, Modales)
        <>
          <Header
            onLoginClick={() => setShowLogin(true)}
            onReservasClick={() => setShowReservas(true)}
            onVehiculosClick={() => setShowVehiculos(true)} // Conectamos el botón de vehículos
            user={user}
            onLogout={handleLogout}
          />

          <section style={{ height: 'calc(100vh - 60px)', width: '100%', position: 'relative' }}>
            <MapComponent 
              user={user}
              onReserveClick={handleReservarClick}
            />
          </section>

          {/* --- MODALES --- */}
          
          {showLogin && (
            <Login
              onClose={() => setShowLogin(false)}
              onLoginSuccess={handleLoginSuccess}
            />
          )}

          {showReservaModal && estacionSeleccionada && (
            <ReservaModal
              estacion={estacionSeleccionada}
              user={user}
              onClose={() => {
                setShowReservaModal(false);
                setEstacionSeleccionada(null);
              }}
            />
          )}

          {showReservas && (
            <MisReservas
              user={user}
              onClose={() => setShowReservas(false)}
            />
          )}

          {/* Modal de Vehículos (Solo si hay usuario logueado) */}
          {showVehiculos && user && (
            <VehiculosEV
              user={user}
              onClose={() => setShowVehiculos(false)}
            />
          )}
        </>
      )}
    </div>
  );
}

export default App;