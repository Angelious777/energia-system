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

    theme: "dark"
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
                "BAJA",
                "MEDIA",
                "ALTA",
                "CRÍTICA"
            ],

            datasets: [{

                label: "Alertas",

                data: [0,0,0,0],

                backgroundColor: [

                    "#22c55e",
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

    let baja = 0;
    let media = 0;
    let alta = 0;
    let critica = 0;

    alertas.forEach(alerta => {

        const sev =
            (alerta.severidad || "")
                .toUpperCase();

        if (sev === "BAJA") baja++;
        else if (sev === "MEDIA") media++;
        else if (sev === "ALTA") alta++;
        else if (sev === "CRITICA") critica++;
        else alta++;

    });

    const chart =
        state.charts.alert;

    chart.data.labels = [
        "BAJA",
        "MEDIA",
        "ALTA",
        "CRÍTICA"
    ];

    chart.data.datasets[0].data = [

        baja,
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
                    ${(device.consumo || 0)
                        .toFixed(2)} kWh
                </strong>

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
                    ${(device.consumo || 0)
                        .toFixed(2)}
                </td>

                <td>
                    Ahora
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

    container.innerHTML =
        data.map(item => `

            <div class="recommendation-card">

                <h4>
                    ${item.dispositivo_id}
                </h4>

                <p>
                    ${item.recomendacion}
                </p>

            </div>

        `).join("");

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

