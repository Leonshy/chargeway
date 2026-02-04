import React, { useState, useEffect } from "react";
import "./AdminPanel.css";

function AdminPanel({ user, onClose }) {
  const [models, setModels] = useState([]);
  const [currentModel, setCurrentModel] = useState(null); // ✅ Cambiado a null inicial
  const [data, setData] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [alert, setAlert] = useState({ show: false, message: "", type: "" });

  // ✅ PASO 1: Verificar si el usuario es admin
  useEffect(() => {
    checkAdmin();
  }, []);

  // ✅ PASO 2: Cargar modelos y stats cuando se verifica admin
  useEffect(() => {
    if (!loading) {
      loadModels();
      loadStats();
    }
  }, [loading]);

  // ✅ PASO 3: Cargar datos cuando cambia el modelo o la página
  useEffect(() => {
    if (currentModel) {
      loadData();
    }
  }, [currentModel, currentPage, searchTerm]);

  const checkAdmin = async () => {
    try {
      const response = await fetch("/api/admin/check-admin", {
        credentials: "include"
      });
      const result = await response.json();

      if (!result.is_admin) {
        showAlert("No tienes permisos de administrador", "error");
        setTimeout(() => onClose(), 2000);
        return;
      }

      setLoading(false);
    } catch (error) {
      console.error("Error verificando permisos:", error);
      showAlert("Error al verificar permisos", "error");
      setTimeout(() => onClose(), 2000);
    }
  };

  const loadModels = async () => {
    try {
      const response = await fetch("/api/admin/models", {
        credentials: "include"
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("Modelos cargados:", result); // ✅ Debug
      setModels(result);

      // ✅ Establecer el primer modelo SOLO si aún no hay uno seleccionado
      if (result.length > 0 && !currentModel) {
        setCurrentModel(result[0].key);
      }
    } catch (error) {
      console.error("Error cargando modelos:", error);
      showAlert("Error al cargar modelos", "error");
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch("/api/admin/stats", {
        credentials: "include"
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("Estadísticas cargadas:", result); // ✅ Debug
      setStats(result);
    } catch (error) {
      console.error("Error cargando estadísticas:", error);
      // ✅ NO mostrar alerta al usuario, solo log en consola
      // showAlert("Error al cargar estadísticas", "error");
    }
  };

  const loadData = async () => {
    try {
      const url = `/api/admin/data/${currentModel}?page=${currentPage}&per_page=20${searchTerm ? `&search=${searchTerm}` : ""
        }`;

      console.log("Cargando datos desde:", url); // ✅ Debug

      const response = await fetch(url, {
        credentials: "include"
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("Datos cargados:", result); // ✅ Debug

      setData(result.data || []);
      setTotalPages(result.pages || 1);
    } catch (error) {
      console.error("Error cargando datos:", error);
      showAlert("Error al cargar datos: " + error.message, "error");
      setData([]);
    }
  };

  const handleCreate = () => {
    setEditingItem(null);
    setShowModal(true);
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    // ✅ Protección: No permitir eliminar el usuario admin actual
    if (currentModel === "usuarios") {
      const itemToDelete = data.find(item => item.id === id);
      if (itemToDelete && itemToDelete.id === user.id) {
        showAlert("No puedes eliminarte a ti mismo", "error");
        return;
      }
      if (itemToDelete && itemToDelete.role === "admin") {
        if (!confirm("⚠️ ADVERTENCIA: Estás eliminando un usuario ADMINISTRADOR. ¿Estás completamente seguro?")) {
          return;
        }
      }
    }

    if (!confirm("¿Estás seguro de eliminar este registro?")) return;

    try {
      const response = await fetch(`/api/admin/data/${currentModel}/${id}`, {
        method: "DELETE",
        credentials: "include"
      });

      if (response.ok) {
        showAlert("Registro eliminado exitosamente", "success");
        await loadData();
        // ✅ Cargar stats y modelos de forma segura sin bloquear la UI
        loadStats().catch(err => console.error("Error cargando stats:", err));
        loadModels().catch(err => console.error("Error cargando modelos:", err));
      } else {
        const result = await response.json();
        showAlert(result.error || "Error al eliminar", "error");
      }
    } catch (error) {
      console.error("Error al eliminar registro:", error);
      showAlert("Error al eliminar registro: " + error.message, "error");
    }
  };

  const handleExport = async () => {
    try {
      const response = await fetch(`/api/admin/export/${currentModel}`, {
        credentials: "include"
      });
      const result = await response.json();

      const blob = new Blob([JSON.stringify(result, null, 2)], {
        type: "application/json"
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${currentModel}_${new Date().toISOString()}.json`;
      a.click();

      showAlert("Datos exportados exitosamente", "success");
    } catch (error) {
      showAlert("Error al exportar datos", "error");
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const showAlert = (message, type) => {
    setAlert({ show: true, message, type });
    setTimeout(() => {
      setAlert({ show: false, message: "", type: "" });
    }, 5000);
  };

  const getModelConfig = () => {
    return models.find((m) => m.key === currentModel);
  };

  const renderTableHeaders = () => {
    const modelConfig = getModelConfig();
    if (!modelConfig) return null;

    const fields = Object.entries(modelConfig.fields).slice(0, 6);

    return (
      <tr>
        {fields.map(([key, field]) => (
          <th key={key}>{field.label}</th>
        ))}
        <th>Acciones</th>
      </tr>
    );
  };

  const renderTableRow = (item) => {
    const modelConfig = getModelConfig();
    if (!modelConfig) return null;

    const fields = Object.entries(modelConfig.fields).slice(0, 6);

    // ✅ Verificar si es el usuario actual para deshabilitar el botón de eliminar
    const isCurrentUser = currentModel === "usuarios" && item.id === user.id;
    const isAdmin = currentModel === "usuarios" && item.role === "admin";

    return (
      <tr key={item.id}>
        {fields.map(([key, field]) => (
          <td key={key}>{formatValue(item[key], key)}</td>
        ))}
        <td className="actions-cell">
          <button
            className="btn-edit"
            onClick={() => handleEdit(item)}
            title="Editar"
          >
            ✏️
          </button>
          <button
            className="btn-delete"
            onClick={() => handleDelete(item.id)}
            title={isCurrentUser ? "No puedes eliminarte a ti mismo" : "Eliminar"}
            disabled={isCurrentUser}
            style={{
              opacity: isCurrentUser ? 0.5 : 1,
              cursor: isCurrentUser ? "not-allowed" : "pointer"
            }}
          >
            🗑️
          </button>
          {isCurrentUser && (
            <span style={{ fontSize: "0.7rem", color: "#666", marginLeft: "5px" }}>
              (Tú)
            </span>
          )}
        </td>
      </tr>
    );
  };

  const formatValue = (value, key) => {
    if (key === "estado") {
      const badges = {
        activa: "badge-success",
        completada: "badge-info",
        cancelada: "badge-danger"
      };
      return <span className={`badge ${badges[value] || "badge-info"}`}>{value}</span>;
    }

    if (key === "role") {
      const badges = {
        admin: "badge-warning",
        user: "badge-info"
      };
      return <span className={`badge ${badges[value] || "badge-info"}`}>{value}</span>;
    }

    if (typeof value === "boolean") {
      return value ? "✅ Sí" : "❌ No";
    }

    if (value === null || value === undefined) {
      return "-";
    }

    return value;
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <p>Cargando panel de administración...</p>
      </div>
    );
  }

  return (
    <div className="admin-overlay" onClick={onClose}>
      <div className="admin-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="admin-header">
          <div className="admin-header-content">
            <h1>⚡ Panel de Administración</h1>
            <div className="admin-user-info">
              <span className="admin-username">👤 {user.username}</span>
              <span className="badge badge-warning">Admin</span>
              <button className="btn-close" onClick={onClose}>
                ✕
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="stats-grid">
            <div className="stat-card stat-users">
              <h3>👤 Usuarios</h3>
              <div className="stat-value">{stats.usuarios?.total || 0}</div>
              <div className="stat-detail">Activos: {stats.usuarios?.activos || 0}</div>
            </div>
            <div className="stat-card stat-reservas">
              <h3>📅 Reservas</h3>
              <div className="stat-value">{stats.reservas?.total || 0}</div>
              <div className="stat-detail">Activas: {stats.reservas?.activas || 0}</div>
            </div>
            <div className="stat-card stat-estaciones">
              <h3>⚡ Estaciones</h3>
              <div className="stat-value">{stats.estaciones?.total || 0}</div>
              <div className="stat-detail">Activas: {stats.estaciones?.activas || 0}</div>
            </div>
            <div className="stat-card stat-vehiculos">
              <h3>🚗 Vehículos</h3>
              <div className="stat-value">{stats.vehiculos?.total || 0}</div>
              <div className="stat-detail">
                Registrados: {stats.vehiculos?.registrados || 0}
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="admin-tabs">
          {models.map((model) => (
            <button
              key={model.key}
              className={`admin-tab ${currentModel === model.key ? "active" : ""}`}
              onClick={() => {
                setCurrentModel(model.key);
                setCurrentPage(1);
              }}
            >
              {model.icon} {model.name} ({model.count})
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="admin-content">
          {/* Toolbar */}
          <div className="admin-toolbar">
            <div className="search-box">
              <input
                type="text"
                placeholder="Buscar..."
                value={searchTerm}
                onChange={handleSearch}
              />
            </div>
            <div className="toolbar-actions">
              <button className="btn-primary" onClick={handleCreate}>
                + Crear Nuevo
              </button>
              <button className="btn-success btn-small" onClick={handleExport}>
                📊 Exportar
              </button>
              <button className="btn-secondary btn-small" onClick={loadData}>
                🔄 Recargar
              </button>
            </div>
          </div>

          {/* Alert */}
          {alert.show && (
            <div className={`alert alert-${alert.type}`}>{alert.message}</div>
          )}

          {/* Table */}
          <div className="table-container">
            {data.length === 0 ? (
              <div className="no-data">
                <p>No hay registros para mostrar</p>
              </div>
            ) : (
              <table className="admin-table">
                <thead>{renderTableHeaders()}</thead>
                <tbody>{data.map((item) => renderTableRow(item))}</tbody>
              </table>
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(currentPage - 1)}
              >
                ← Anterior
              </button>

              {[...Array(Math.min(5, totalPages))].map((_, i) => {
                const pageNum = i + 1;
                return (
                  <button
                    key={pageNum}
                    className={currentPage === pageNum ? "active" : ""}
                    onClick={() => setCurrentPage(pageNum)}
                  >
                    {pageNum}
                  </button>
                );
              })}

              <button
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(currentPage + 1)}
              >
                Siguiente →
              </button>
            </div>
          )}
        </div>

        {/* Modal */}
        {showModal && (
          <AdminModal
            model={currentModel}
            modelConfig={getModelConfig()}
            item={editingItem}
            onClose={() => {
              setShowModal(false);
              setEditingItem(null);
            }}
            onSuccess={() => {
              setShowModal(false);
              setEditingItem(null);
              loadData();
              loadStats();
              loadModels();
              showAlert(
                editingItem
                  ? "Registro actualizado exitosamente"
                  : "Registro creado exitosamente",
                "success"
              );
            }}
          />
        )}
      </div>
    </div>
  );
}

// ============================================
// COMPONENTE MODAL
// ============================================
function AdminModal({ model, modelConfig, item, onClose, onSuccess }) {
  const [formData, setFormData] = useState(item || {});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? e.target.checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const url = item
      ? `/api/admin/data/${model}/${item.id}`
      : `/api/admin/data/${model}`;
    const method = item ? "PUT" : "POST";

    try {
      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (response.ok) {
        onSuccess();
      } else {
        setError(result.error || "Error al guardar");
      }
    } catch (err) {
      setError("Error de conexión");
    } finally {
      setLoading(false);
    }
  };

  const renderField = ([key, field]) => {
    if (field.readonly && item) return null;

    const value = formData[key] || field.default || "";

    if (field.type === "select") {
      return (
        <div className="form-group" key={key}>
          <label>
            {field.label}
            {field.required && " *"}
          </label>
          <select
            name={key}
            value={value}
            onChange={handleChange}
            required={field.required}
          >
            <option value="">Seleccionar...</option>
            {field.options.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>
      );
    }

    if (field.type === "boolean") {
      return (
        <div className="form-group" key={key}>
          <label>
            <input
              type="checkbox"
              name={key}
              checked={value === true || value === "true"}
              onChange={(e) =>
                setFormData({ ...formData, [key]: e.target.checked })
              }
            />
            {field.label}
          </label>
        </div>
      );
    }

    return (
      <div className="form-group" key={key}>
        <label>
          {field.label}
          {field.required && " *"}
        </label>
        <input
          type={field.type}
          name={key}
          value={value}
          onChange={handleChange}
          required={field.required}
        />
      </div>
    );
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{item ? "Editar Registro" : "Crear Nuevo Registro"}</h2>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          {Object.entries(modelConfig.fields)
            .filter(([key, field]) => !(field.readonly && item))
            .map((entry) => renderField(entry))}

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Guardando..." : "Guardar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AdminPanel;