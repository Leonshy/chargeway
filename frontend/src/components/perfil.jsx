import React, { useState, useEffect } from "react";

function Perfil({ user, onClose, onUpdateSuccess }) {
  const [formData, setFormData] = useState({
    username: "",
    phone: "",
    current_password: "",
    new_password: "",
  });

  // Estados de Vehículo
  const [brands, setBrands] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedBrand, setSelectedBrand] = useState("");
  const [selectedAutoId, setSelectedAutoId] = useState("");
  const [currentVehicle, setCurrentVehicle] = useState(null); // Para mostrar el actual

  const [msg, setMsg] = useState(null);

  // Inicializar
  useEffect(() => {
    if (user) {
      setFormData(prev => ({ ...prev, username: user.username, phone: user.phone || "" }));
      fetchBrands();
      fetchCurrentVehicle();
    }
  }, [user]);

  // Cargar Marcas
  const fetchBrands = async () => {
    try {
      const res = await fetch("/api/vehiculos/brands");
      if (res.ok) setBrands(await res.json());
    } catch (e) { console.error(e); }
  };

  // Cargar Vehículo Actual (El que ya tiene registrado)
  const fetchCurrentVehicle = async () => {
    try {
      const res = await fetch("/api/vehiculos/current"); // Nueva ruta específica
      if (res.ok) {
        const data = await res.json();
        setCurrentVehicle(data); 
        // No pre-seleccionamos en los combos para obligar al usuario a elegir si quiere cambiar
        // Si quieres que aparezca pre-seleccionado, descomenta esto:
        /*
        if (data) {
           setSelectedBrand(data.marca);
           fetchModels(data.marca);
           setSelectedAutoId(data.id);
        }
        */
      }
    } catch (e) { console.error(e); }
  };

  const handleBrandChange = (e) => {
    const brand = e.target.value;
    setSelectedBrand(brand);
    setModels([]);
    setSelectedAutoId("");
    if (brand) fetchModels(brand);
  };

  const fetchModels = async (brand) => {
    try {
      const res = await fetch(`/api/vehiculos/models/${brand}`);
      if (res.ok) setModels(await res.json());
    } catch (e) { console.error(e); }
  };

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.current_password) return setMsg({ error: true, text: "Ingresa contraseña actual" });

    try {
      // 1. Actualizar Datos Usuario
      const resUser = await fetch("/api/users/update", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData),
      });
      const dataUser = await resUser.json();

      if (!resUser.ok) {
        setMsg({ error: true, text: dataUser.error });
        return;
      }

      // 2. Actualizar Vehículo (Solo si seleccionó uno nuevo)
      if (selectedAutoId) {
        await fetch("/api/vehiculos/assign", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ autos_id: selectedAutoId }),
        });
      }

      onUpdateSuccess(dataUser.user);
      setMsg({ error: false, text: "¡Perfil guardado correctamente!" });
      setTimeout(onClose, 1500);

    } catch (err) {
      setMsg({ error: true, text: "Error de conexión" });
    }
  };

  // Estilos
  const s = {
    overlay: { position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.6)", zIndex: 3000, display: "flex", justifyContent: "center", alignItems: "center" },
    modal: { background: "white", padding: "20px", borderRadius: "12px", width: "320px", maxWidth: "90%", maxHeight: "85vh", overflowY: "auto", position: "relative", boxShadow: "0 10px 25px rgba(0,0,0,0.2)" },
    input: { width: "100%", padding: "8px", margin: "5px 0 10px", border: "1px solid #ccc", borderRadius: "6px", boxSizing: "border-box", fontSize: "0.9rem" },
    label: { fontSize: "0.85rem", fontWeight: "600", color: "#333", display: "block", marginTop: "5px" },
    btn: { width: "100%", padding: "10px", background: "#007bff", color: "white", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold", marginTop: "15px" },
    close: { position: "absolute", top: "10px", right: "15px", background: "none", border: "none", fontSize: "1.5rem", cursor: "pointer", color: "#666" },
    currentCar: { background: "#e3f2fd", padding: "8px", borderRadius: "6px", fontSize: "0.85rem", color: "#0d47a1", marginBottom: "10px", border: "1px solid #90caf9" }
  };

  return (
    <div style={s.overlay} onClick={onClose}>
      <div style={s.modal} onClick={(e) => e.stopPropagation()}>
        <button style={s.close} onClick={onClose}>×</button>
        <h3 style={{marginTop: 0, textAlign: "center", color: "#333"}}>Mi Perfil</h3>

        {msg && <div style={{padding: "8px", marginBottom: "10px", borderRadius: "4px", textAlign: "center", background: msg.error ? "#ffebee" : "#e8f5e9", color: msg.error ? "#c62828" : "#2e7d32", fontSize: "0.85rem"}}>{msg.text}</div>}

        <form onSubmit={handleSubmit}>
          <label style={s.label}>Usuario</label>
          <input name="username" value={formData.username} onChange={handleChange} style={s.input} required />

          <label style={s.label}>Teléfono</label>
          <input name="phone" value={formData.phone} onChange={handleChange} style={s.input} placeholder="+56 9..." />

          <hr style={{margin: "15px 0", borderTop: "1px solid #eee"}} />
          
          <h4 style={{fontSize: "0.95rem", margin: "0 0 10px 0", color: "#007bff"}}>Mi Vehículo</h4>
          
          {/* Mostrar Vehículo Actual */}
          {currentVehicle ? (
            <div style={s.currentCar}>
              <strong>Actual:</strong> {currentVehicle.marca} {currentVehicle.modelo} ({currentVehicle.anio})
            </div>
          ) : (
            <div style={{...s.currentCar, background: "#f5f5f5", color: "#666", border: "1px solid #ddd"}}>
              No tienes vehículo registrado.
            </div>
          )}

          <label style={s.label}>Cambiar Vehículo:</label>
          <select value={selectedBrand} onChange={handleBrandChange} style={s.input}>
            <option value="">-- Seleccionar Marca --</option>
            {brands.map((b, i) => <option key={i} value={b}>{b}</option>)}
          </select>

          <select 
            value={selectedAutoId} 
            onChange={(e) => setSelectedAutoId(e.target.value)} 
            style={s.input}
            disabled={!models.length}
          >
            <option value="">-- Seleccionar Modelo --</option>
            {models.map(m => (
              <option key={m.id} value={m.id}>
                {m.modelo} ({m.anio}) {m.bateria !== "N/A" ? `- ${m.bateria}` : ""}
              </option>
            ))}
          </select>

          <hr style={{margin: "15px 0", borderTop: "1px solid #eee"}} />

          <label style={s.label}>Nueva Contraseña (Opcional)</label>
          <input type="password" name="new_password" value={formData.new_password} onChange={handleChange} style={s.input} placeholder="••••••" />

          <label style={{...s.label, color: "#d32f2f"}}>Contraseña Actual (Requerido)</label>
          <input type="password" name="current_password" value={formData.current_password} onChange={handleChange} style={s.input} required />

          <button type="submit" style={s.btn}>Guardar Cambios</button>
        </form>
      </div>
    </div>
  );
}

export default Perfil;