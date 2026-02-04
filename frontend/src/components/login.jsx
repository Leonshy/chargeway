import React, { useState, useRef } from "react";
import ReCAPTCHA from "react-google-recaptcha";

function Login({ onClose, onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const recaptchaRef = useRef(null);

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    phone: ""
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    // ============================================
    // ✅ VALIDAR CAPTCHA SOLO EN REGISTRO
    // ============================================
    let recaptchaToken = null;
    if (isRegister) {
      recaptchaToken = recaptchaRef.current?.getValue();
      
      if (!recaptchaToken) {
        setError("Por favor, completa el captcha");
        setLoading(false);
        return;
      }
    }

    const url = isRegister ? "/api/auth/register" : "/api/auth/login";
    const body = isRegister
      ? { ...formData, recaptcha_token: recaptchaToken }
      : { email: formData.email, password: formData.password };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (response.ok) {
        onLoginSuccess(data.user);
        onClose();
      } else {
        setError(data.error || "Error en la autenticación");
        // Resetear captcha si falla
        if (isRegister && recaptchaRef.current) {
          recaptchaRef.current.reset();
        }
      }
    } catch (err) {
      setError("Error de conexión con el servidor");
      console.error(err);
      // Resetear captcha en caso de error
      if (isRegister && recaptchaRef.current) {
        recaptchaRef.current.reset();
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSwitchMode = () => {
    setIsRegister(!isRegister);
    setError("");
    // Resetear captcha al cambiar de modo
    if (recaptchaRef.current) {
      recaptchaRef.current.reset();
    }
  };

  return (
    <div className="login-overlay" onClick={onClose}>
      <div className="login-box" onClick={(e) => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>
          ✕
        </button>

        <h2>{isRegister ? "Registrarse" : "Iniciar Sesión"}</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <input
              type="text"
              name="username"
              placeholder="Usuario"
              value={formData.username}
              onChange={handleChange}
              required
            />
          )}

          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            type="password"
            name="password"
            placeholder="Contraseña"
            value={formData.password}
            onChange={handleChange}
            required
          />

          {isRegister && (
            <input
              type="tel"
              name="phone"
              placeholder="Teléfono (opcional)"
              value={formData.phone}
              onChange={handleChange}
            />
          )}

          {/* ============================================ */}
          {/* 🔒 CAPTCHA - SOLO VISIBLE EN REGISTRO */}
          {/* ============================================ */}
          {isRegister && (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              margin: '15px 0',
              transform: 'scale(0.95)',
              transformOrigin: 'center'
            }}>
              <ReCAPTCHA
                ref={recaptchaRef}
                sitekey="6Lc-OGAsAAAAAFXfaThay_SxNnmibOPyoocQR5Di" // 👈 REEMPLAZA CON TU SITE KEY
                theme="light"
              />
            </div>
          )}

          <button type="submit" className="login-btn" disabled={loading}>
            {loading
              ? "Procesando..."
              : isRegister
                ? "Registrarse"
                : "Iniciar Sesión"}
          </button>
        </form>

        <p className="switch-text">
          {isRegister ? "¿Ya tienes cuenta?" : "¿No tienes cuenta?"}{" "}
          <span onClick={handleSwitchMode}>
            {isRegister ? "Inicia sesión aquí" : "Regístrate aquí"}
          </span>
        </p>
      </div>
    </div>
  );
}

export default Login;