// ========================================
// CONFIG
// ========================================

const API_BASE = window.location.origin;

const REFRESH_INTERVAL = 2000;

const state = {

    activeView: "dashboard",

    charts: {},

    polling: null,

    lastAlerts: new Set(),

    theme: "dark",

    devices: []
};

// ========================================
// INIT
// ========================================

document.addEventListener("DOMContentLoaded", () => {

    initializeSystem();

});

// ========================================
// SYSTEM
// ========================================

function initializeSystem() {

    hideLoading();

    initializeTheme();

    initializeSidebar();

    initializeDateTime();

    initializeCharts();

    initializeToast();

    initializeEstadisticas();

    initializeAlertas();

    startPolling();

}

// ========================================
// LOADING
// ========================================

function hideLoading() {

    setTimeout(() => {

        const loading = document.getElementById(
            "loadingScreen"
        );

        loading.style.opacity = "0";

        setTimeout(() => {

            loading.style.display = "none";

        }, 600);

    }, 1800);

}

// ========================================
// THEME
// ========================================

function initializeTheme() {

    const savedTheme =
        localStorage.getItem("theme") || "dark";

    applyTheme(savedTheme);

    document
        .getElementById("themeToggle")
        .addEventListener("click", toggleTheme);

}

function toggleTheme() {

    const nextTheme =
        state.theme === "dark"
            ? "light"
            : "dark";

    applyTheme(nextTheme);

}

function applyTheme(theme) {

    state.theme = theme;

    document.body.classList.toggle(
        "light-theme",
        theme === "light"
    );

    localStorage.setItem(
        "theme",
        theme
    );

}

// ========================================
// SIDEBAR
// ========================================

function initializeSidebar() {

    const buttons =
        document.querySelectorAll(".menu-item");

    buttons.forEach(button => {

        button.addEventListener("click", () => {

            const view =
                button.dataset.view;

            setActiveView(view);

        });

    });

}

function setActiveView(view) {

    state.activeView = view;

    document
        .querySelectorAll(".menu-item")
        .forEach(btn => {

            btn.classList.toggle(
                "active",
                btn.dataset.view === view
            );

        });

    document
        .querySelectorAll(".view")
        .forEach(section => {

            section.classList.toggle(
                "hidden",
                section.id !== `view-${view}`
            );

        });

}

// ========================================
// DATETIME
// ========================================

function initializeDateTime() {

    updateDateTime();

    setInterval(
        updateDateTime,
        1000
    );

    // Cargar dispositivos iniciales
    cargarDispositivosIniciales();

}

function updateDateTime() {

    const now = new Date();

    document.getElementById(
        "currentDate"
    ).textContent = now.toLocaleDateString(
        "es-ES",
        {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }
    );

    document.getElementById(
        "currentTime"
    ).textContent = now.toLocaleTimeString(
        "es-ES"
    );

}

// ========================================
// FETCH
// ========================================

async function fetchJson(path) {

    const response =
        await fetch(`${API_BASE}${path}`);

    if (!response.ok) {

        throw new Error(
            `Error ${response.status}`
        );

    }

    return response.json();

}

// ========================================
// POLLING
// ========================================

function startPolling() {

    loadData();

    if (state.polling) {

        clearInterval(state.polling);

    }

    state.polling = setInterval(
        loadData,
        REFRESH_INTERVAL
    );

}

// ========================================
// LOAD DATA
// ========================================

async function loadData() {

    try {

        let today =
            new Date()
                .toISOString()
                .split("T")[0];

        let [

            dashboard,

            alertas,

            dispositivos,

            recomendaciones,

            zonas

        ] = await Promise.all([

            fetchJson(`/dashboard/${today}`),

            fetchJson(`/alertas/${today}`),

            fetchJson(`/dispositivos/${today}`),

            fetchJson(`/recomendaciones/${today}`),

            fetchJson(`/zonas/${today}`)

        ]);

        // If today has no usable data, try yesterday
        const hasTodayData =
            alertas.length > 0 ||
            (dashboard && dashboard.alertas_hoy > 0) ||
            (zonas && zonas.labels && zonas.labels.length > 0) ||
            (dispositivos && dispositivos.length > 0);

        if (!hasTodayData) {

            const yesterday = new Date(
                Date.now() - 86400000
            ).toISOString().split("T")[0];

            [

                dashboard,

                alertas,

                dispositivos,

                recomendaciones,

                zonas

            ] = await Promise.all([

                fetchJson(
                    `/dashboard/${yesterday}`
                ),

                fetchJson(
                    `/alertas/${yesterday}`
                ),

                fetchJson(
                    `/dispositivos/${yesterday}`
                ),

                fetchJson(
                    `/recomendaciones/${yesterday}`
                ),

                fetchJson(`/zonas/${yesterday}`)

            ]);

        }

        updateKPIs(
            dashboard,
            alertas,
            dispositivos
        );

        updateCharts(
            dashboard,
            alertas,
            zonas
        );

        renderAlerts(alertas);

        renderDevices(dispositivos);

        renderRecommendations(
            recomendaciones.recomendaciones || []
        );

        renderHistory(alertas);

        renderZones(zonas);

        updateInfrastructure();

    }

    catch (error) {

        console.error(
            "Error cargando datos:",
            error
        );

    }

}

// ========================================
// KPIs
// ========================================

function updateKPIs(
    dashboard,
    alertas,
    dispositivos
) {

    const totalConsumo =
        dashboard.total_consumo ||
        dashboard.consumo_total ||
        0;

    document.getElementById(
        "kpiConsumo"
    ).textContent =
        `${totalConsumo.toFixed(2)} kWh`;

    document.getElementById(
        "kpiDispositivos"
    ).textContent =
        dispositivos.length || 0;

    document.getElementById(
        "kpiAlertas"
    ).textContent =
        alertas.length || 0;

    document.getElementById(
        "sidebarAlertCount"
    ).textContent =
        alertas.length || 0;

    if (dispositivos.length > 0) {

        document.getElementById(
            "kpiZona"
        ).textContent =
            dispositivos[0].zona || "--";

    }

}

// ========================================
// CHARTS
// ========================================

function initializeCharts() {

    initializeMainChart();

    initializeZoneChart();

    initializeAlertChart();

    initializeTrendChart();

}

function initializeMainChart() {

    const ctx =
        document.getElementById(
            "mainChart"
        ).getContext("2d");

    state.charts.main = new Chart(ctx, {

        type: "line",

        data: {

            labels: [],

            datasets: [{

                label: "Consumo",

                data: [],

                borderColor: "#3b82f6",

                backgroundColor:
                    "rgba(59,130,246,0.15)",

                fill: true,

                tension: 0.4

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

}

function initializeZoneChart() {

    const ctx =
        document.getElementById(
            "zoneChart"
        ).getContext("2d");

    state.charts.zone = new Chart(ctx, {

        type: "doughnut",

        data: {

            labels: [],

            datasets: [{

                data: [],

                backgroundColor: [

                    "#3b82f6",
                    "#22c55e",
                    "#f59e0b",
                    "#ef4444",
                    "#8b5cf6"

                ]

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

}

function initializeAlertChart() {

    const ctx =
        document.getElementById(
            "alertChart"
        ).getContext("2d");

    state.charts.alert = new Chart(ctx, {

        type: "bar",

        data: {

            labels: [
                "MEDIA",
                "ALTA",
                "CRÍTICA"
            ],

            datasets: [{

                label: "Alertas",

                data: [0,0,0],

                backgroundColor: [

                    "#f59e0b",
                    "#ef4444",
                    "#991b1b"

                ]

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

}

function initializeTrendChart() {

    const ctx =
        document.getElementById(
            "trendChart"
        ).getContext("2d");

    state.charts.trend = new Chart(ctx, {

        type: "line",

        data: {

            labels: [],

            datasets: [{

                label: "Tendencia",

                data: [],

                borderColor: "#22c55e",

                backgroundColor:
                    "rgba(34,197,94,0.15)",

                fill: true,

                tension: 0.4

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

}

// ========================================
// UPDATE CHARTS
// ========================================

function updateCharts(
    dashboard,
    alertas,
    zonas
) {

    updateMainChart(dashboard);

    updateZoneChart(zonas);

    updateAlertChart(alertas);

    updateTrendChart(zonas);

}

function updateMainChart(dashboard) {

    const chart =
        state.charts.main;

    const now =
        new Date().toLocaleTimeString(
            "es-ES",
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        );

    chart.data.labels.push(now);

    chart.data.datasets[0].data.push(
        dashboard.total_consumo ||
        dashboard.consumo_total ||
        0
    );

    if (chart.data.labels.length > 12) {

        chart.data.labels.shift();

        chart.data.datasets[0].data.shift();

    }

    chart.update();

}

function updateZoneChart(zonas) {

    const chart =
        state.charts.zone;

    chart.data.labels =
        zonas.labels || [];

    chart.data.datasets[0].data =
        zonas.values || [];

    chart.update();

}

function updateAlertChart(alertas) {

    let media = 0;
    let alta = 0;
    let critica = 0;

    alertas.forEach(alerta => {

        const sev =
            (alerta.severidad || "")
                .toUpperCase();

        if (sev === "MEDIA") media++;
        else if (sev === "ALTA") alta++;
        else if (sev === "CRITICA") critica++;
        else if (sev === "BAJA") {
            // No contar BAJA
        } else alta++;  // Default to alta

    });

    const chart =
        state.charts.alert;

    chart.data.labels = [
        "MEDIA",
        "ALTA",
        "CRÍTICA"
    ];

    chart.data.datasets[0].data = [

        media,
        alta,
        critica

    ];

    chart.update();

}

function updateTrendChart(zonas) {

    const chart =
        state.charts.trend;

    chart.data.labels =
        zonas.tendencia?.labels || [];

    chart.data.datasets[0].data =
        zonas.tendencia?.values || [];

    chart.update();

}

// ========================================
// ALERTS
// ========================================

function renderAlerts(alertas) {

    const container =
        document.getElementById(
            "alertsContainer"
        );

    const grid =
        document.getElementById(
            "alertsGrid"
        );

    if (!alertas.length) {

        container.innerHTML =
            "<p>Sin alertas</p>";

        grid.innerHTML =
            "<p>Sin alertas</p>";

        return;

    }

    const html = alertas.map(alerta => {

        const key =
            `${alerta.dispositivo_id}_${alerta.timestamp}`;

        if (!state.lastAlerts.has(key)) {

            showToast(
                "Nueva alerta",
                alerta.dispositivo_id
            );

            state.lastAlerts.add(key);

        }

        return `

            <div class="alert-card">

                <div class="alert-top">

                    <h4>
                        ${alerta.dispositivo_id}
                    </h4>

                    <span class="severity ${alerta.severidad}">
                        ${alerta.severidad}
                    </span>

                </div>

                <p>
                    Zona:
                    ${alerta.zona}
                </p>

                <p>
                    Consumo:
                    ${Number(alerta.consumo)
                        .toFixed(2)} kWh
                </p>

                <small>
                    ${formatDate(alerta.timestamp)}
                </small>

            </div>

        `;

    }).join("");

    container.innerHTML = html;

    grid.innerHTML = html;

}

// ========================================
// DEVICES
// ========================================

function renderDevices(dispositivos) {

    const top =
        document.getElementById(
            "topDevices"
        );

    const tbody =
        document.getElementById(
            "devicesTableBody"
        );

    if (!dispositivos.length) {

        top.innerHTML =
            "<p>Sin dispositivos</p>";

        tbody.innerHTML =
            "<tr><td colspan=6>Sin dispositivos</td></tr>";

        return;

    }

    top.innerHTML = dispositivos
        .slice(0,5)
        .map(device => `

            <div class="device-card">

                <h4>
                    ${device.dispositivo_id}
                </h4>

                <p>
                    ${device.zona}
                </p>

                <strong>
                    ${device.consumo_total.toFixed(2)} kWh total
                </strong>

                <small>
                    ${device.consumo_actual.toFixed(2)} kWh actual
                </small>

            </div>

        `)
        .join("");

    tbody.innerHTML =
        dispositivos.map((device,index) => `

            <tr>

                <td>${index+1}</td>

                <td>
                    ${device.dispositivo_id}
                </td>

                <td>
                    ${device.zona}
                </td>

                <td>
                    Activo
                </td>

                <td>
                    ${device.consumo_total.toFixed(2)} / ${device.consumo_actual.toFixed(2)} kWh
                </td>

                <td>
                    ${device.ultimo_evento}
                </td>

            </tr>

        `).join("");

}

// ========================================
// RECOMMENDATIONS
// ========================================

function renderRecommendations(data) {

    const container =
        document.getElementById(
            "recommendationsGrid"
        );

    if (!data.length) {

        container.innerHTML =
            "<p>Sin recomendaciones</p>";

        return;

    }

    // Usar Map para evitar duplicados por dispositivo_id
    const uniqueRecommendations = new Map();

    data.forEach(item => {
        uniqueRecommendations.set(item.dispositivo_id, item);
    });

    const html = Array.from(uniqueRecommendations.values()).map(item => `

        <div class="alert-card recommendation">

            <div class="alert-top">

                <h4>
                    ${item.dispositivo_id}
                </h4>

                <span class="severity info">
                    RECOMENDACIÓN
                </span>

            </div>

            <p>
                ${item.recomendacion}
            </p>

            <small>
                Optimización automática
            </small>

        </div>

    `).join("");

    container.innerHTML = html;

}

// ========================================
// ESTADISTICAS
// ========================================

function renderEstadisticas(estadisticas) {

    const container =
        document.getElementById(
            "estadisticasGrid"
        );

    if (!estadisticas || !estadisticas.length) {

        container.innerHTML =
            "<p>Sin estadísticas disponibles</p>";

        return;

    }

    const html = estadisticas.map(estadistica => `

        <div class="stat-card">

            <div class="stat-header">

                <h4>
                    Zona ${estadistica.zona}
                </h4>

                <i class="fas fa-chart-bar"></i>

            </div>

            <div class="stat-body">

                <div class="stat-metric">

                    <span class="label">
                        Consumo Total
                    </span>

                    <span class="value">
                        ${estadistica.total_consumo.toFixed(2)} kWh
                    </span>

                </div>

                <div class="stat-metric">

                    <span class="label">
                        Promedio
                    </span>

                    <span class="value">
                        ${estadistica.promedio.toFixed(2)} kWh
                    </span>

                </div>

            </div>

        </div>

    `).join("");

    container.innerHTML = html;

}

// ========================================
// HISTORY
// ========================================

function renderHistory(alertas) {

    const table =
        document.getElementById(
            "historyTable"
        );

    if (!alertas.length) {
        table.innerHTML =
            `<tr><td colspan="6">Sin registros históricos</td></tr>`;
        return;
    }

    table.innerHTML =
        alertas.map((a,index) => `

            <tr>

                <td>${index+1}</td>

                <td>
                    ${a.dispositivo_id || "-"}
                </td>

                <td>
                    ${a.zona || "-"}
                </td>

                <td>
                    ${(a.consumo || 0)
                        .toFixed(2)}
                </td>

                <td>
                    ${a.severidad || "-"}
                </td>

                <td>
                    ${a.timestamp ? formatDate(a.timestamp) : "-"}
                </td>

            </tr>

        `).join("");

}

// ========================================
// ZONES
// ========================================

function renderZones(zonas) {

    const labels =
        zonas.labels || [];

    const valores =
        zonas.values || [];

    const zoneIdMap = {
        "centro": "zonaCentro",
        "sur": "zonaSur",
        "norte": "zonaNorte",
        "el alto": "zonaAlto",
        "alto": "zonaAlto"
    };

    labels.forEach((zona,index) => {

        const normalized = zona
            .trim()
            .toLowerCase();

        const id =
            zoneIdMap[normalized] ||
            `zona${normalized.replace(/\s+/g, "")}`;

        const element =
            document.getElementById(id);

        if (element) {

            element.textContent =
                `${(valores[index] || 0).toFixed(2)} kWh`;

        }

    });

    const zoneMap = document.getElementById("zoneMap");

    if (zoneMap) {

        zoneMap.innerHTML = labels.map((zona,index) => `
            <div class="map-zone">
                <h4>${zona}</h4>
                <strong>${(valores[index] || 0).toFixed(2)} kWh</strong>
                <p>
                    ${(valores[index] || 0) > 0 ? "Consumo actual" : "Sin datos"}
                </p>
            </div>
        `).join("");

    }

}

// ========================================
// INFRA
// ========================================

function updateInfrastructure() {

    document.getElementById(
        "apiStatus"
    ).textContent = "Disponible";

    document.getElementById(
        "redisStatus"
    ).textContent = "Activo";

    document.getElementById(
        "workerStatus"
    ).textContent = "Procesando";

    document.getElementById(
        "cassandraStatus"
    ).textContent = "Conectado";

}

// ========================================
// DISPOSITIVOS REALTIME
// ========================================

function actualizarDispositivoRealtime(data) {

    if (!state.devices) {
        state.devices = [];
    }

    const indice = state.devices.findIndex(
        d => d.dispositivo_id === data.dispositivo_id
    );

    if (indice >= 0) {
        // Actualizar dispositivo existente
        state.devices[indice].consumo_actual = data.consumo_actual || 0;
        state.devices[indice].ultimo_evento = data.timestamp;
    } else {
        // Agregar nuevo dispositivo
        state.devices.push({
            dispositivo_id: data.dispositivo_id,
            consumo_actual: data.consumo_actual || 0,
            ultimo_evento: data.timestamp,
            consumo_total: 0,
            zona: "DESCONOCIDA"
        });
    }

    // Ordenar por consumo total
    state.devices.sort((a, b) => b.consumo_total - a.consumo_total);

    // Re-renderizar tabla completa
    renderDevices(state.devices);

}

function cargarDispositivosIniciales() {

    let today = new Date()
        .toISOString()
        .split("T")[0];

    fetchJson(`/dispositivos/${today}`)
        .then(dispositivos => {
            if (Array.isArray(dispositivos)) {
                state.devices = dispositivos;
                renderDevices(state.devices);
            }
        })
        .catch(error => {
            console.error("Error cargando dispositivos:", error);
        });

}

// ========================================
// TOAST
// ========================================

function initializeToast() {

    document
        .getElementById("toastClose")
        .addEventListener(
            "click",
            hideToast
        );

}

function showToast(
    title,
    message
) {

    document.getElementById(
        "toastTitle"
    ).textContent = title;

    document.getElementById(
        "toastMessage"
    ).textContent = message;

    document
        .getElementById("mainToast")
        .classList.add("show");

    setTimeout(
        hideToast,
        5000
    );

}

function hideToast() {

    document
        .getElementById("mainToast")
        .classList.remove("show");

}

// ========================================
// ESTADISTICAS INIT
// ========================================

function initializeEstadisticas() {

    // Set default date to today
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("estadisticasFecha").value = today;

    // Add event listener for calculate button
    document
        .getElementById("btnCalcularEstadisticas")
        .addEventListener("click", async () => {

            const fecha = document.getElementById("estadisticasFecha").value;

            if (!fecha) {
                showToast("Error", "Selecciona una fecha");
                return;
            }

            try {
                const response = await fetch(`/estadisticas/zona/${fecha}`);
                const data = await response.json();

                if (data.estadisticas) {
                    renderEstadisticas(data.estadisticas);
                } else {
                    renderEstadisticas([]);
                }

            } catch (error) {
                console.error("Error cargando estadísticas:", error);
                showToast("Error", "No se pudieron cargar las estadísticas");
            }

        });

    document
        .getElementById("btnGuardarEstadisticas")
        .addEventListener("click", async () => {

            const zona = document.getElementById("estadisticasZona").value.trim();
            const fecha = document.getElementById("estadisticasFecha").value;

            if (!zona || !fecha) {
                showToast("Error", "Completa zona y fecha");
                return;
            }

            try {
                const response = await fetch(
                    `/estadisticas/zona/${zona}/${fecha}/calcular`,
                    {
                        method: "POST"
                    }
                );

                const data = await response.json();

                if (response.ok) {
                    showToast("Éxito", "Estadística guardada en Cassandra");
                    // Refrescar lista de estadísticas
                    document.getElementById("btnCalcularEstadisticas").click();
                } else {
                    showToast("Error", data.error || "No se pudo guardar");
                }

            } catch (error) {
                console.error("Error guardando estadística:", error);
                showToast("Error", "No se pudo guardar la estadística");
            }

        });

}

function initializeAlertas() {

    document
        .getElementById("btnGuardarAlertaDispositivo")
        .addEventListener("click", async () => {

            const dispositivo_id = document.getElementById("alertaDispositivoId").value.trim();
            const zona = document.getElementById("alertaZona").value.trim();
            const consumo = parseFloat(document.getElementById("alertaConsumo").value.trim());
            const severidad = document.getElementById("alertaSeveridad").value.trim().toUpperCase();
            const mensaje = document.getElementById("alertaMensaje").value.trim();
            const fecha = new Date().toISOString();

            if (!dispositivo_id || !zona || Number.isNaN(consumo) || !severidad || !mensaje) {
                showToast("Error", "Completa todos los campos");
                return;
            }

            try {
                const response = await fetch(
                    "/alertas/dispositivo",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            dispositivo_id,
                            zona,
                            consumo,
                            severidad,
                            recomendacion: mensaje,
                            timestamp: fecha
                        })
                    }
                );

                const data = await response.json();

                if (response.ok) {
                    showToast("Éxito", "Alerta guardada en Cassandra");
                    document.getElementById("alertaDispositivoId").value = "";
                    document.getElementById("alertaZona").value = "";
                    document.getElementById("alertaConsumo").value = "";
                    document.getElementById("alertaSeveridad").value = "";
                    document.getElementById("alertaMensaje").value = "";
                } else {
                    showToast("Error", data.error || "No se pudo guardar la alerta");
                }

            } catch (error) {
                console.error("Error guardando alerta:", error);
                showToast("Error", "No se pudo guardar la alerta");
            }

        });

}

// ========================================
// UTIL
// ========================================

function formatDate(value) {

    if (!value) return "--";

    return new Date(value)
        .toLocaleString("es-ES");

}

function capitalize(text) {

    return text.charAt(0)
        .toUpperCase() + text.slice(1);

}

