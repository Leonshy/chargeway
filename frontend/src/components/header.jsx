import React, { useState } from "react";

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header>
      {/* Lado izquierdo: hamburguesa + logo */}
      <div className="header-left">
        <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)}>
          <span></span>
          <span></span>
          <span></span>
        </button>
        <div className="logo" >
          <img src=".\src\components\logo.png"></img>
        </div>
      </div>

      {/* Lado derecho: login */}
      <div className="header-right">
        <button>Login</button>
      </div>

      {/* Menú desplegable */}
      {menuOpen && (
        <div className="menu-dropdown">
          <p>Item 1</p>
          <p>Item 2</p>
          <p>Item 3</p>
        </div>
      )}
    </header>
  );
}

function App() {
  return (
    <div className="relative">
      <Header />          {/* tu header con menú y login */}
      <MapSection />      {/* el mapa generado por Flask */}
      <button className="find-station-button">Encontrar Estación</button>
    </div>
  );
}

