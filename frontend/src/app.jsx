import React, { useState, useEffect } from "react";
import Header from "./components/header";
<<<<<<< HEAD
import Login from "./components/Login";
import MapComponent from "./components/mapcomponent";
import ReservaModal from "./components/ReservaModal"; // Asegúrate que el nombre coincida con tu archivo
import MisReservas from "./components/MisReservas";   // Asegúrate que el nombre coincida con tu archivo
import AdminPanel from "./adminPanel";     // <--- 1. IMPORTAR ADMIN

// --- CONFIGURACIÓN: CORREO DEL ADMINISTRADOR ---
const ADMIN_EMAIL = "admin@chargeway.com"; // <--- CAMBIA ESTO POR TU EMAIL REAL
=======
import Login from "./components/login";
import MapComponent from "./components/MapComponent";
import ReservaModal from "./components/ReservaModal";
import MisReservas from "./components/MisReservas";
import VehiculosEV from "./components/vehiculo"; // ← NUEVO IMPORT
>>>>>>> 7ad02abede2dd237b1f228f39e1ca6989e39eb0a

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [showReservas, setShowReservas] = useState(false);
  const [showVehiculos, setShowVehiculos] = useState(false); // ← NUEVO ESTADO
  const [showReservaModal, setShowReservaModal] = useState(false);
  const [estacionSeleccionada, setEstacionSeleccionada] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [vistaActual, setVistaActual] = useState('mapa');

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    setShowLogin(false);
    
    // Si el que entra NO es admin, forzamos la vista al mapa por seguridad
    if (userData.email !== ADMIN_EMAIL) {
        setVistaActual('mapa');
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    setShowReservas(false);
    setVistaActual('mapa'); // Al salir, volver al mapa
  };

  const handleReservarClick = (estacion) => {
    if (!user) {
      setShowLogin(true);
    } else {
      setEstacionSeleccionada(estacion);
      setShowReservaModal(true);
    }
  };

  // Verificamos si es admin para usarlo en el renderizado
  const isAdmin = user && user.email === ADMIN_EMAIL;

  if (loading) {
    return <div style={{ color: 'green', padding: '20px' }}>Cargando Chargeway...</div>;
  }

  return (
<<<<<<< HEAD
    <div style={{ height: '100vh', overflow: 'hidden', position: 'relative' }}>
      
      {/* --- BOTÓN DE ADMIN (SOLO VISIBLE PARA EL ADMIN) --- */}
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
=======
    <div style={{ height: '100vh', overflow: 'hidden' }}>
      <Header
        onLoginClick={() => setShowLogin(true)}
        onReservasClick={() => setShowReservas(true)}
        onVehiculosClick={() => setShowVehiculos(true)} // ← NUEVA PROP
        user={user}
        onLogout={handleLogout}
      />

      <section style={{
        position: 'relative',
        height: 'calc(100vh - 60px)',
        width: '100%',
        overflow: 'hidden'
      }}>
      <MapComponent
        user={user}
        onReserveClick={handleReserveClick}
      />

      </section>

      {/* MODAL LOGIN */}
      {showLogin && (
        <Login
          onClose={() => setShowLogin(false)}
          onLoginSuccess={handleLoginSuccess}
        />
>>>>>>> 7ad02abede2dd237b1f228f39e1ca6989e39eb0a
      )}

      {/* --- RENDERIZADO PROTEGIDO --- */}
      {isAdmin && vistaActual === 'admin' ? (
        // Solo mostramos el panel si es admin Y está en la vista correcta
        <AdminPanel />
      ) : (
        // Vista normal para todos los demás
        <>
          <Header
            onLoginClick={() => setShowLogin(true)}
            onReservasClick={() => setShowReservas(true)}
            user={user}
            onLogout={handleLogout}
          />

          <section style={{ height: 'calc(100vh - 60px)', width: '100%', position: 'relative' }}>
            <MapComponent 
              user={user}
              onReserveClick={handleReservarClick}
            />
          </section>

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
        </>
      )}

      {/* MODAL MIS VEHÍCULOS - NUEVO */}
      {showVehiculos && user && (
        <VehiculosEV
          user={user}
          onClose={() => setShowVehiculos(false)}
        />
      )}
    </div>
  );
}

export default App;