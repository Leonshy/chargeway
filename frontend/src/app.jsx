import React, { useState, useEffect } from "react";
import Header from "./components/header";
import Login from "./components/Login";

function App() {
  const [mapaHTML, setMapaHTML] = useState("");
  const [showLogin, setShowLogin] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);

  // Manejar cambios en el tamaño de la ventana (importante para móviles)
  useEffect(() => {
    const handleResize = () => {
      setWindowHeight(window.innerHeight);
    };

    window.addEventListener('resize', handleResize);
    // También detectar cambios de orientación
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

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

  // Cargar el mapa desde el backend
  useEffect(() => {
    fetch("/api/mapa")
      .then((res) => res.text())
      .then((html) => setMapaHTML(html))
      .catch((err) => console.error("Error al cargar el mapa:", err));
  }, []);

  // Manejar login exitoso
  const handleLoginSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
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
        user={user}
        onLogout={handleLogout}
      />

      <section style={{
        position: 'relative',
        height: 'calc(100vh - 60px)',
        width: '100%',
        overflow: 'hidden'
      }}>
        <div
          id="mapa"
          style={{
            width: '100%',
            height: '100%',
            position: 'relative'
          }}
          dangerouslySetInnerHTML={{ __html: mapaHTML }}
        ></div>

        <button className="find-station-button">
          Encontrar Estación
        </button>
      </section>

      {/* MODAL LOGIN */}
      {showLogin && (
        <Login
          onClose={() => setShowLogin(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      )}
    </div>
  );
}

export default App;