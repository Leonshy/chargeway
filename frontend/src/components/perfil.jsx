import React, { useState, useEffect } from "react";

function Perfil({ user, onClose, onUpdateSuccess }) {
  const [formData, setFormData] = useState({
    username: "",
    phone: "",
    current_password: "",
    new_password: "",
  });
  const [msg, setMsg] = useState(null);

  useEffect(() => {
    if (user) {
      setFormData(prev => ({ ...prev, username: user.username, phone: user.phone || "" }));
    }
  }, [user]);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.current_password) return setMsg({ error: true, text: "Ingresa tu contraseña actual" });

    try {
      const res = await fetch("/api/users/update", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      
      if (res.ok) {
        onUpdateSuccess(data.user);
        setMsg({ error: false, text: "¡Actualizado!" });
        setTimeout(onClose, 1000);
      } else {
        setMsg({ error: true, text: data.error });
      }
    } catch (err) {
      setMsg({ error: true, text: "Error de conexión" });
    }
  };

  // Estilos inline para asegurar compacidad
  const styles = {
    overlay: {
      position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: "rgba(0,0,0,0.6)", zIndex: 2000,
      display: "flex", justifyContent: "center", alignItems: "center"
    },
    modal: {
      backgroundColor: "white", padding: "15px 20px", borderRadius: "10px",
      width: "300px", maxWidth: "90%", boxShadow: "0 4px 15px rgba(0,0,0,0.3)",
      position: "relative", fontFamily: "Arial, sans-serif"
    },
    input: {
      width: "100%", padding: "8px", margin: "5px 0 10px",
      fontSize: "0.85rem", border: "1px solid #ccc", borderRadius: "4px",
      boxSizing: "border-box"
    },
    label: { fontSize: "0.8rem", fontWeight: "bold", color: "#444", display: "block" },
    btn: {
      width: "100%", padding: "8px", backgroundColor: "#007bff", color: "white",
      border: "none", borderRadius: "4px", cursor: "pointer", fontSize: "0.9rem",
      marginTop: "10px", fontWeight: "bold"
    },
    close: {
      position: "absolute", top: "10px", right: "10px", background: "none",
      border: "none", fontSize: "1.2rem", cursor: "pointer", color: "#666"
    }
  };

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button style={styles.close} onClick={onClose}>✕</button>
        <h3 style={{margin: "0 0 15px 0", textAlign: "center", fontSize: "1.1rem"}}>Editar Perfil</h3>
        
        {msg && <div style={{
          padding: "5px", marginBottom: "10px", borderRadius: "4px", fontSize: "0.75rem", 
          textAlign: "center", backgroundColor: msg.error ? "#ffebee" : "#e8f5e9", 
          color: msg.error ? "#c62828" : "#2e7d32"
        }}>{msg.text}</div>}

        <form onSubmit={handleSubmit}>
          <label style={styles.label}>Nombre de usuario</label>
          <input type="text" name="username" value={formData.username} onChange={handleChange} style={styles.input} required />

          <label style={styles.label}>Teléfono</label>
          <input type="tel" name="phone" value={formData.phone} onChange={handleChange} style={styles.input} placeholder="+56 9..." />

          <label style={styles.label}>Nueva Contraseña (Opcional)</label>
          <input type="password" name="new_password" value={formData.new_password} onChange={handleChange} style={styles.input} placeholder="********" />

          <hr style={{margin: "10px 0", borderTop: "1px solid #eee"}}/>

          <label style={{...styles.label, color: "#d32f2f"}}>Contraseña Actual (Para confirmar)</label>
          <input type="password" name="current_password" value={formData.current_password} onChange={handleChange} style={styles.input} required />

          <button type="submit" style={styles.btn}>Guardar</button>
        </form>
      </div>
    </div>
  );
}

export default Perfil;