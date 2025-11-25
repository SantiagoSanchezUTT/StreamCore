// ----------------------
// VARIABLES GLOBALES
// ----------------------
let plataformaActual = "twitch";
let asistenciaBD = [];
let asistenciaFiltrada = [];
let autoRefreshEnabled = false;

// ----------------------
// UTILIDAD PARA ESCAPAR HTML
// ----------------------
function escapeHtml(text) {
    return text.replace(/[&<>"']/g, function(m) {
        return ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[m];
    });
}

// ----------------------
// CAMBIO DE PLATAFORMA
// ----------------------
function seleccionarPlataforma(plataforma) {
    plataformaActual = plataforma;

    document.querySelectorAll(".platform-btn").forEach(btn =>
        btn.classList.remove("selected")
    );

    document.querySelector(`.platform-btn[data-platform="${plataforma}"]`)
        ?.classList.add("selected");

    renderizarTabla();
}

window.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".platform-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            seleccionarPlataforma(btn.dataset.platform);
        });
    });
});

// ----------------------
// CARGAR ASISTENCIAS
// ----------------------
async function cargarAsistenciasBD() {
    if (!window.pywebview?.api) return;

    try {
        const res = await window.pywebview.api.get_asistencias();

        if (res?.success && Array.isArray(res.data)) {
            asistenciaBD = res.data;
            renderizarTabla();
        }

    } catch (err) {
        console.error("Error cargando asistencias", err);
    }
}

// ----------------------
// RENDERIZAR TABLA
// ----------------------
function renderizarTabla() {
    const tbody = document.getElementById("tablaAsistencias");
    if (!tbody) return;

    tbody.innerHTML = "";

    asistenciaFiltrada = asistenciaBD.filter(
        item => item.platform === plataformaActual
    );

    const filtro = document.getElementById("buscador").value.toLowerCase();
    let lista = asistenciaFiltrada;

    if (filtro) {
        lista = lista.filter(item =>
            item.nickname.toLowerCase().includes(filtro)
        );
    }

    const orden = document.getElementById("ordenar").value;

    if (orden === "nombre") {
        lista.sort((a, b) => a.nickname.localeCompare(b.nickname));
    } else {
        lista.sort((a, b) => b.total_asistencias - a.total_asistencias);
    }

    if (lista.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="3" class="px-4 py-4 text-gray-400">
                No hay registros para ${plataformaActual}
            </td></tr>`;
        return;
    }

    lista.forEach(item => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td class="px-4 py-3">${escapeHtml(item.nickname)}</td>
            <td class="px-4 py-3">${item.total_asistencias}</td>
            <td class="px-4 py-3">
                <button class="btn-action primary" onclick="editarAsistencia(${item.id}, '${item.nickname}')">
                    Editar
                </button>
                <button class="btn-action danger" onclick="eliminarAsistencia(${item.id})">
                    Eliminar
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

// ----------------------
// EDITAR
// ----------------------
async function editarAsistencia(id, nickname) {
    const nuevo = prompt(`Editar asistencias de ${nickname}:`);
    if (nuevo === null) return;

    const num = parseInt(nuevo);
    if (isNaN(num) || num < 0) return alert("Valor inválido");

    const res = await window.pywebview.api.editar_asistencia(id, num);

    if (res.success) {
        cargarAsistenciasBD();
    } else {
        alert("Error: " + res.error);
    }
}

// ----------------------
// ELIMINAR
// ----------------------
async function eliminarAsistencia(id) {
    if (!confirm("¿Eliminar registro?")) return;

    const res = await window.pywebview.api.delete_asistencia(id);

    if (res.success) {
        cargarAsistenciasBD();
    } else {
        alert("Error: " + res.error);
    }
}

// ----------------------
// AUTO-REFRESH INTELIGENTE
// ----------------------
function activarAutoRefresh() {
    if (autoRefreshEnabled) return;
    autoRefreshEnabled = true;

    // Método A — eventos nativos pywebview (si existen)
    if (window.pywebview?.on) {
        window.pywebview.on("asistencias:updated", () => {
            cargarAsistenciasBD();
        });
        console.log("Auto-refresh activado con pywebview.on");
        return;
    }

    // Método B — fallback seguro con polling
    console.log("pywebview.on no disponible — usando polling cada 1s.");
    setInterval(() => {
        cargarAsistenciasBD();
    }, 1000);
}

// ----------------------
// EVENTO: pywebview listo
// ----------------------
window.addEventListener("pywebviewready", () => {
    cargarAsistenciasBD();
    activarAutoRefresh();
});

// Buscador y orden
window.addEventListener("DOMContentLoaded", () => {
    document.getElementById("buscador").addEventListener("input", renderizarTabla);
    document.getElementById("ordenar").addEventListener("change", renderizarTabla);
});
