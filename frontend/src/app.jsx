import React, { useState, useEffect } from "react";
import Header from "./components/header";

function App() {
  const [mapaHTML, setMapaHTML] = useState("");

  useEffect(() => {
    // Endpoint de Flask que devuelve el HTML del mapa
    fetch("http://127.0.0.1:5000/")
      .then((res) => res.text())
      .then((html) => setMapaHTML(html))
      .catch((err) => console.error("Error al cargar el mapa:", err));
  }, []);

  return (
    <div className="relative">
      <Header />

      <section className="relative w-full h-[80vh]">
        <div
          id="mapa"
          className="w-full h-full"
          dangerouslySetInnerHTML={{ __html: mapaHTML }}
        ></div>

        <button className="find-station-button absolute bottom-4 right-4 p-2 bg-blue-500 text-white rounded">
          Encontrar Estación
        </button>
      </section>
    </div>
  );
}

export default App;
