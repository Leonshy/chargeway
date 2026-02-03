import React, { useState, useEffect, useRef } from "react";

function Header({ onLoginClick, onReservasClick, user, onLogout }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const menuRef = useRef(null);
  const buttonRef = useRef(null);

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
    if (!menuOpen) return;

    const handleClickOutside = (event) => {
      if (
        menuRef.current && 
        !menuRef.current.contains(event.target) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target)
      ) {
        setMenuOpen(false);
      }
    };

    // Esperar un tick antes de agregar el listener
    const timeoutId = setTimeout(() => {
      document.addEventListener('mousedown', handleClickOutside);
    }, 0);

    return () => {
      clearTimeout(timeoutId);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuOpen]);

  const handleMenuClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setMenuOpen(prev => !prev);
  };

  const handleReservasClick = () => {
    setMenuOpen(false);
    if (onReservasClick) {
      onReservasClick();
    }
  };

  return (
    <header>
      <div className="header-left">
        {/* Menú hamburguesa */}
        <button
          ref={buttonRef}
          className="menu-button"
          onClick={handleMenuClick}
          aria-label="Menú"
          type="button"
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
        <div ref={menuRef} className="menu-dropdown">
          <p onClick={() => setMenuOpen(false)}>🗺️ Mapa</p>
          {user && (
            <p onClick={handleReservasClick}>📋 Mis Reservas</p>
          )}
          <p onClick={() => setMenuOpen(false)}>🚗 Vehículos EV</p>
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