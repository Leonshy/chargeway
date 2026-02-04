import React from "react";
import "./Header.css";

function Header({
  onLoginClick,
  onReservasClick,
  onVehiculosClick,
  onAcercaDeClick,
  onAdminClick,
  onKioskClick, // 🆕 NUEVA PROP para abrir el Kiosk
  user,
  onLogout,
  isAdmin
}) {
  return (
    <header className="header">
      <div className="header-container">
        {/* Logo y título */}
        <div className="header-logo">
          <i className="fa-solid fa-bolt"></i>
          <h1>ChargeWay</h1>
        </div>

        {/* Navegación y botones */}
        <nav className="header-nav">
          {user ? (
            <>
              {/* Información del usuario */}
              <div className="header-user-info">
                <i className="fa-solid fa-user-circle"></i>
                <span>{user.username}</span>
              </div>

              {/* Botones de navegación */}
              <button
                onClick={onReservasClick}
                className="header-btn btn-reservas"
                title="Ver mis reservas"
              >
                <i className="fa-solid fa-calendar-check"></i>
                <span>Mis Reservas</span>
              </button>

              <button
                onClick={onVehiculosClick}
                className="header-btn btn-vehiculos"
                title="Gestionar mis vehículos"
              >
                <i className="fa-solid fa-car"></i>
                <span>Mis Vehículos</span>
              </button>

              <button
                onClick={onAcercaDeClick}
                className="header-btn btn-info"
                title="Acerca de ChargeWay"
              >
                <i className="fa-solid fa-info-circle"></i>
                <span>Acerca de</span>
              </button>

              {/* 🆕 NUEVO: Botón Kiosk de Estación */}
              <button
                onClick={onKioskClick}
                className="header-btn btn-kiosk"
                title="Modo Terminal de Estación"
              >
                <i className="fa-solid fa-charging-station"></i>
                <span>Modo Estación</span>
              </button>

              {/* Botón Admin (solo para administradores) */}
              {isAdmin && (
                <button
                  onClick={onAdminClick}
                  className="header-btn btn-admin"
                  title="Panel de Administración"
                >
                  <i className="fa-solid fa-user-shield"></i>
                  <span>Admin Panel</span>
                </button>
              )}

              {/* Botón Cerrar Sesión */}
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
            <>
              {/* Usuario no logueado */}
              <button
                onClick={onAcercaDeClick}
                className="header-btn btn-info"
                title="Acerca de ChargeWay"
              >
                <i className="fa-solid fa-info-circle"></i>
                <span>Acerca de</span>
              </button>

              {/* 🆕 Botón Kiosk disponible sin login */}
              <button
                onClick={onKioskClick}
                className="header-btn btn-kiosk"
                title="Modo Terminal de Estación"
              >
                <i className="fa-solid fa-charging-station"></i>
                <span>Modo Estación</span>
              </button>

              <button
                onClick={onLoginClick}
                className="header-btn btn-login"
                title="Iniciar sesión"
              >
                <i className="fa-solid fa-sign-in-alt"></i>
                <span>Iniciar Sesión</span>
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Header;
