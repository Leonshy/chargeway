import React, { useState } from "react";
import "./Header.css";

function Header({
  onLoginClick,
  onReservasClick,
  onVehiculosClick,
  onAcercaDeClick,
  onAdminClick,
  onKioskClick,
  user,
  onLogout,
  isAdmin
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const handleMenuItemClick = (callback) => {
    callback();
    setMenuOpen(false); // Cierra el menú después de hacer clic
  };

  return (
    <header className="header">
      <div className="header-container">
        {/* Menú Hamburguesa + Logo */}
        <div className="header-left">
          <button 
            className={`hamburger-btn ${menuOpen ? 'active' : ''}`}
            onClick={toggleMenu}
            aria-label="Menú"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>

          <div className="header-logo">
            <i className="fa-solid fa-bolt"></i>
            <h1>ChargeWay</h1>
          </div>
        </div>

        {/* Menú Desplegable */}
        <nav className={`dropdown-menu ${menuOpen ? 'open' : ''}`}>
          <button
            onClick={() => handleMenuItemClick(onReservasClick)}
            className="menu-item"
          >
            <i className="fa-solid fa-calendar-check"></i>
            <span>Mis Reservas</span>
          </button>

          <button
            onClick={() => handleMenuItemClick(onVehiculosClick)}
            className="menu-item"
          >
            <i className="fa-solid fa-car"></i>
            <span>Mis Vehículos</span>
          </button>

          <button
            onClick={() => handleMenuItemClick(onAcercaDeClick)}
            className="menu-item"
          >
            <i className="fa-solid fa-info-circle"></i>
            <span>Acerca de</span>
          </button>

          <button
            onClick={() => handleMenuItemClick(onKioskClick)}
            className="menu-item"
          >
            <i className="fa-solid fa-charging-station"></i>
            <span>Modo Estación</span>
          </button>

          {/* Botón Admin (solo para administradores) */}
          {isAdmin && (
            <button
              onClick={() => handleMenuItemClick(onAdminClick)}
              className="menu-item menu-item-admin"
            >
              <i className="fa-solid fa-user-shield"></i>
              <span>Admin Panel</span>
            </button>
          )}
        </nav>

        {/* Overlay para cerrar el menú al hacer clic fuera */}
        {menuOpen && (
          <div 
            className="menu-overlay" 
            onClick={() => setMenuOpen(false)}
          ></div>
        )}

        {/* Usuario y Botón Salir (derecha) */}
        <div className="header-right">
          {user ? (
            <>
              <div className="header-user-info">
                <i className="fa-solid fa-user-circle"></i>
                <span>{user.username}</span>
              </div>
              <button
                onClick={onLogout}
                className="header-btn btn-logout"
                title="Cerrar sesión"
              >
                <i className="fa-solid fa-sign-out-alt"></i>
                <span>Salir</span>
              </button>
            </>
          ) : (
            <button
              onClick={onLoginClick}
              className="header-btn btn-login"
              title="Iniciar sesión"
            >
              <i className="fa-solid fa-sign-in-alt"></i>
              <span>Iniciar Sesión</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;