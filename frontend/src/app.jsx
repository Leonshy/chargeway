import React, { useState, useEffect } from "react";
import Header from "./components/header";
import Login from "./components/login";

function App() {
  const [mapaHTML, setMapaHTML] = useState("");
  const [showLogin, setShowLogin] = useState(false);

  useEffect(() => {
    // Endpoint de Flask que devuelve el HTML del mapa
    fetch("http://127.0.0.1:5000/")
      .then((res) => res.text())
      .then((html) => setMapaHTML(html))
      .catch((err) => console.error("Error al cargar el mapa:", err));
  }, []);

  return (
    <div>
      <Header onLoginClick={() => setShowLogin(true)} />

      <section>
        <div
          id="mapa"
          dangerouslySetInnerHTML={{ __html: mapaHTML }}
        ></div>

        <button className="find-station-button">
          Encontrar Estación
        </button>
      </section>

      {/* MODAL LOGIN */}
      {showLogin && (
      <Login onClose={() => setShowLogin(false)} />)}

    </div>
      
  );
}

export default App;
