import React, { useState, useEffect, useRef } from "react";

function Header({
  onLoginClick,
  onReservasClick,
  onVehiculosClick,
  onAcercaDeClick,
  onAdminClick, // 🆕 NUEVO
  user,
  onLogout,
  isAdmin // 🆕 NUEVO
}) {
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
    window.addEventListener("resize", checkMobile);

    return () => window.removeEventListener("resize", checkMobile);
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

    document.addEventListener("click", handleClickOutside, true);

    return () => {
      document.removeEventListener("click", handleClickOutside, true);
    };
  }, [menuOpen]);

  const handleMenuClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setMenuOpen((prev) => !prev);
  };

  const handleReservasClick = () => {
    setMenuOpen(false);
    if (onReservasClick) {
      onReservasClick();
    }
  };

  const handleVehiculosClick = () => {
    setMenuOpen(false);
    if (onVehiculosClick) {
      onVehiculosClick();
    }
  };

  const handleAcercaDeClick = () => {
    setMenuOpen(false);
    if (onAcercaDeClick) {
      onAcercaDeClick();
    }
  };

  // 🆕 NUEVO: Handler para panel admin
  const handleAdminClick = () => {
    setMenuOpen(false);
    if (onAdminClick) {
      onAdminClick();
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
          {user && (
            <>
              <p onClick={handleReservasClick}>📅 Mis Reservas</p>
              <p onClick={handleVehiculosClick}>🚗 Mis Vehículos</p>

              {/* 🆕 NUEVO: Mostrar Panel Admin solo si es admin */}
              {isAdmin && (
                <>
                  <div style={{ borderTop: "1px solid #e2e8f0", margin: "0.5rem 0" }} />
                  <p
                    onClick={handleAdminClick}  // ← Debe ser onClick
                    style={{
                      background: "linear-gradient(135deg, #667eea, #764ba2)",
                      color: "white",
                      borderRadius: "6px",
                      padding: "0.75rem 1rem",
                      fontWeight: "600",
                      cursor: "pointer"  // ← Agregar cursor pointer
                    }}
                  >
                    🔐 Panel de Administración
                  </p>
                </>
              )}
            </>
          )}

          <p onClick={handleAcercaDeClick}>ℹ️ Acerca de</p>
        </div>
      )}

      <div className="header-right">
        {user ? (
          <div
            style={{
              display: "flex",
              gap: isMobile ? "0.5rem" : "1rem",
              alignItems: "center",
              flexDirection: isMobile ? "column" : "row"
            }}
          >
            <span style={{ color: "#00c853" }}>
              👤 {isMobile ? user.username.substring(0, 10) : user.username}
              {/* 🆕 NUEVO: Badge de admin */}
              {isAdmin && (
                <span
                  style={{
                    marginLeft: "0.5rem",
                    background: "#fbbf24",
                    color: "#78350f",
                    padding: "0.2rem 0.5rem",
                    borderRadius: "999px",
                    fontSize: "0.75rem",
                    fontWeight: "600"
                  }}
                >
                  ADMIN
                </span>
              )}
            </span>
            <button onClick={onLogout}>
              {isMobile ? "Salir" : "Cerrar Sesión"}
            </button>
          </div>
        ) : (
          <button onClick={onLoginClick}>
            {isMobile ? "Login" : "Iniciar Sesión"}
          </button>
        )}
      </div>
    </header>
  );
}

export default Header;
