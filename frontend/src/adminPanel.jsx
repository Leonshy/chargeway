import React, { useState, useEffect } from 'react';
import Header from './components/header';

const AdminPanel = () => {
    const [tables, setTables] = useState([]);
    const [selectedTable, setSelectedTable] = useState(null);
    const [data, setData] = useState([]);
    const [modalOpen, setModalOpen] = useState(false);
    const [currentItem, setCurrentItem] = useState(null);

    // 1. Cargar lista de bases de datos
    useEffect(() => {
        fetch('http://localhost:5000/api/admin/tables')
            .then(res => res.json())
            .then(data => setTables(data));
    }, []);

    // 2. Cargar datos de la tabla seleccionada
    const loadData = (table) => {
        setSelectedTable(table);
        setData([]); // Limpiamos data antes de cargar nueva para evitar errores visuales
        fetch(`http://localhost:5000/api/admin/data/${table}`)
            .then(res => res.json())
            .then(responseData => {
                // Si la respuesta es un array, todo bien. Si es error, lo guardamos igual.
                setData(responseData);
            })
            .catch(err => {
                console.error(err);
                setData({ error: "Error de conexión con el servidor" });
            });
    };

    // --- ACCIONES (Delete, Save) ---
    const handleDelete = (id) => {
        if(!window.confirm("¿Seguro que quieres eliminar este dato?")) return;
        fetch(`http://localhost:5000/api/admin/data/${selectedTable}/${id}`, { method: 'DELETE' })
            .then(() => loadData(selectedTable));
    };

    const handleSave = (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const jsonData = Object.fromEntries(formData.entries());

        const method = currentItem && currentItem.id ? 'PUT' : 'POST';
        const url = currentItem && currentItem.id 
            ? `http://localhost:5000/api/admin/data/${selectedTable}/${currentItem.id}`
            : `http://localhost:5000/api/admin/data/${selectedTable}`;

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jsonData)
        })
        .then(res => res.json())
        .then(() => {
            setModalOpen(false);
            loadData(selectedTable);
        });
    };

    const openModal = (item = null) => {
        setCurrentItem(item || {});
        setModalOpen(true);
    };

    // Helper para campos del formulario
    const getFormFields = () => {
        if (Array.isArray(data) && data.length > 0) return Object.keys(data[0]);
        // Fallback manual si la lista está vacía
        if (selectedTable === 'usuarios') return ['username', 'email', 'password_hash'];
        if (selectedTable === 'estaciones') return ['Title', 'AddressLine1', 'Latitude', 'Longitude'];
        return ['nombre']; 
    };

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#f4f4f4' }}>
            <Header />
            <div style={{ display: 'flex', padding: '20px', gap: '20px' }}>
                
                {/* BARRA LATERAL */}
                <div style={{ width: '250px', background: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
                    <h3 style={{ color: '#00c853' }}>🗂 Bases de Datos</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {tables.map(table => (
                            <li key={table} style={{ marginBottom: '10px' }}>
                                <button 
                                    onClick={() => loadData(table)}
                                    style={{
                                        width: '100%', padding: '10px', textAlign: 'left',
                                        background: selectedTable === table ? '#00c853' : '#eee',
                                        color: selectedTable === table ? 'white' : 'black',
                                        border: 'none', borderRadius: '5px', cursor: 'pointer',
                                        fontWeight: 'bold', textTransform: 'capitalize'
                                    }}
                                >
                                    {table}
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* CONTENIDO PRINCIPAL */}
                <div style={{ flex: 1, background: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
                    {selectedTable ? (
                        <>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                                <h2 style={{ textTransform: 'capitalize' }}>Gestión de {selectedTable}</h2>
                                <button 
                                    onClick={() => openModal()}
                                    style={{ background: '#007bff', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}
                                >
                                    + Agregar Nuevo
                                </button>
                            </div>

                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ background: '#333', color: 'white' }}>
                                            {/* Header dinámico: Solo si data es array y tiene elementos */}
                                            {Array.isArray(data) && data.length > 0 ? (
                                                Object.keys(data[0]).map(key => (
                                                    <th key={key} style={{ padding: '10px', textAlign: 'left' }}>{key}</th>
                                                ))
                                            ) : (
                                                <th>Info</th>
                                            )}
                                            <th style={{ padding: '10px' }}>Acciones</th>
                                        </tr>
                                    </thead>
                                    
                                    {/* --- AQUÍ ESTÁ LA CORRECCIÓN PRINCIPAL --- */}
                                    <tbody>
                                        {Array.isArray(data) && data.length > 0 ? (
                                            // CASO 1: DATA ES UNA LISTA CORRECTA -> Renderizamos filas
                                            data.map((row, idx) => (
                                                <tr key={idx} style={{ borderBottom: '1px solid #ddd' }}>
                                                    {Object.values(row).map((val, i) => (
                                                        <td key={i} style={{ padding: '10px' }}>{val}</td>
                                                    ))}
                                                    <td style={{ padding: '10px', display: 'flex', gap: '5px' }}>
                                                        <button onClick={() => openModal(row)} style={{ background: '#ffc107', border: 'none', padding: '5px 10px', borderRadius: '3px', cursor: 'pointer' }}>✏️</button>
                                                        <button onClick={() => handleDelete(row.id)} style={{ background: '#dc3545', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '3px', cursor: 'pointer' }}>🗑</button>
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            // CASO 2: DATA ES UN ERROR O ESTÁ VACÍA -> Mostramos mensaje
                                            <tr>
                                                <td colSpan="100%" style={{ textAlign: 'center', padding: '20px', color: data.error ? 'red' : '#666' }}>
                                                    {data.error ? `❌ Error: ${data.error}` : "📭 No hay datos disponibles en esta tabla."}
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                    {/* ----------------------------------------- */}
                                </table>
                            </div>
                        </>
                    ) : (
                        <div style={{ textAlign: 'center', color: '#888', marginTop: '50px' }}>
                            <h3>Selecciona una base de datos del menú izquierdo para comenzar</h3>
                        </div>
                    )}
                </div>
            </div>

            {/* MODAL */}
            {modalOpen && (
                <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <div style={{ background: 'white', padding: '30px', borderRadius: '10px', width: '400px', maxWidth: '90%' }}>
                        <h3>{currentItem.id ? 'Modificar Dato' : 'Agregar Nuevo Dato'}</h3>
                        <form onSubmit={handleSave}>
                            {getFormFields().map(field => {
                                if (field === 'id') return null;
                                return (
                                    <div key={field} style={{ marginBottom: '15px' }}>
                                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>{field}</label>
                                        <input 
                                            name={field}
                                            defaultValue={currentItem[field] || ''}
                                            style={{ width: '100%', padding: '8px', borderRadius: '5px', border: '1px solid #ccc' }}
                                        />
                                    </div>
                                )
                            })}
                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
                                <button type="button" onClick={() => setModalOpen(false)} style={{ background: '#ccc', border: 'none', padding: '10px', borderRadius: '5px', cursor: 'pointer' }}>Cancelar</button>
                                <button type="submit" style={{ background: '#00c853', color: 'white', border: 'none', padding: '10px', borderRadius: '5px', cursor: 'pointer' }}>Guardar</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminPanel;