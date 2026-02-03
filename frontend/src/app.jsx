import React, { useState, useEffect } from "react";
import Header from "./components/header";
import Login from "./components/Login";
import MapComponent from "./components/MapComponent";
import ReservaModal from "./components/ReservaModal";
import MisReservas from "./components/MisReservas";

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [showReservas, setShowReservas] = useState(false);
  const [showReservaModal, setShowReservaModal] = useState(false);
  const [estacionSeleccionada, setEstacionSeleccionada] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Verificar si hay sesión activa al cargar
  useEffect(() => {
    checkAuth();
  }, []);

  // Verificar autenticación
  const checkAuth = async () => {
    try {
      const response = await fetch("/api/auth/check", {
        credentials: "include"
      });

      if (response.ok) {
        const data = await response.json();
        if (data.authenticated) {
          setUser(data.user);
        } else {
          // Intentar cargar desde localStorage
          const savedUser = localStorage.getItem("user");
          if (savedUser) {
            setUser(JSON.parse(savedUser));
          }
        }
      }
    } catch (err) {
      console.error("Error verificando autenticación:", err);
    } finally {
      setLoading(false);
    }
  };

  // Manejar login exitoso
  const handleLoginSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
    setShowLogin(false);
    console.log("Usuario logueado:", userData);
  };

  // Manejar logout
  const handleLogout = async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include"
      });

      setUser(null);
      localStorage.removeItem("user");
      alert("Sesión cerrada correctamente");
    } catch (err) {
      console.error("Error al cerrar sesión:", err);
    }
  };

  // Manejar click en reservar
  const handleReserveClick = (estacion) => {
    setEstacionSeleccionada(estacion);
    setShowReservaModal(true);
  };

  // Manejar éxito de reserva
  const handleReservaSuccess = () => {
    // Puedes agregar lógica adicional aquí si lo necesitas
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '1.2rem',
        color: '#00c853'
      }}>
        <i className="fa-solid fa-bolt"></i>
        <span style={{ marginLeft: '0.5rem' }}>Cargando...</span>
      </div>
    );
  }

  return (
    <div style={{ height: '100vh', overflow: 'hidden' }}>
      <Header
        onLoginClick={() => setShowLogin(true)}
        onReservasClick={() => setShowReservas(true)}
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

        />
      </section>

      {/* MODAL LOGIN */}
      {showLogin && (
        <Login
          onClose={() => setShowLogin(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      )}

      {/* MODAL RESERVA */}
      {showReservaModal && estacionSeleccionada && (
        <ReservaModal
          estacion={estacionSeleccionada}
          onClose={() => {
            setShowReservaModal(false);
            setEstacionSeleccionada(null);
          }}
          onSuccess={handleReservaSuccess}
        />
      )}

      {/* MODAL MIS RESERVAS */}
      {showReservas && user && (
        <MisReservas
          user={user}
          onClose={() => setShowReservas(false)}
        />
      )}
    </div>
  );
}

export default App;