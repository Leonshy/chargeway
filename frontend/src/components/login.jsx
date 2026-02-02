import { useState } from "react";

function Login({ onClose }) {
  const [isRegister, setIsRegister] = useState(false);

  return (
    <div className="login-overlay">
      <div className="login-box">
        <button className="close-btn" onClick={onClose}>✕</button>

        <h2>{isRegister ? "Crear cuenta" : "Iniciar sesión"}</h2>

        {isRegister && (
          <input type="text" placeholder="Nombre de usuario" />
        )}

        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Contraseña" />

        <button className="login-btn">
          {isRegister ? "Registrarse" : "Entrar"}
        </button>

        <p className="switch-text">
          {isRegister ? "¿Ya tenés cuenta?" : "¿No tenés cuenta?"}
          <span onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? " Iniciar sesión" : " Registrarse"}
          </span>
        </p>
      </div>
    </div>
  );
}

export default Login;