import React, { useState, useEffect } from "react";

function Header({ onLoginClick, user, onLogout }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Detectar si es móvil
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Cerrar menú cuando se hace clic fuera
  useEffect(() => {
    const handleClickOutside = () => {
      if (menuOpen) setMenuOpen(false);
    };

    if (menuOpen) {
      document.addEventListener('click', handleClickOutside);
    }

    return () => document.removeEventListener('click', handleClickOutside);
  }, [menuOpen]);

  const handleMenuClick = (e) => {
    e.stopPropagation();
    setMenuOpen(!menuOpen);
  };

  return (
    <header>
      <div className="header-left">
        {/* Menú hamburguesa */}
        <button
          className="menu-button"
          onClick={handleMenuClick}
          aria-label="Menú"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        {/* Logo */}
        <div className="logo">
          <h1>⚡ ChargeWay</h1>
        </div>
      </div>

      {/* Menú desplegable */}
      {menuOpen && (
        <div className="menu-dropdown" onClick={(e) => e.stopPropagation()}>
          <p onClick={() => setMenuOpen(false)}>🗺️ Mapa</p>
          <p onClick={() => setMenuOpen(false)}>🚗 Vehículos EV</p>
          <p onClick={() => setMenuOpen(false)}>📅 Reservas</p>
          <p onClick={() => setMenuOpen(false)}>ℹ️ Acerca de</p>
        </div>
      )}

      <div className="header-right">
        {user ? (
          <div style={{
            display: 'flex',
            gap: isMobile ? '0.5rem' : '1rem',
            alignItems: 'center',
            flexDirection: isMobile ? 'column' : 'row'
          }}>
            <span style={{ color: '#00c853' }}>
              👤 {isMobile ? user.username.substring(0, 10) : user.username}
            </span>
            <button onClick={onLogout}>
              {isMobile ? 'Salir' : 'Cerrar Sesión'}
            </button>
          </div>
        ) : (
          <button onClick={onLoginClick}>
            {isMobile ? 'Login' : 'Iniciar Sesión'}
          </button>
        )}
      </div>
    </header>
  );
}

export default Header;