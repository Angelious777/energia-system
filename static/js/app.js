const API_BASE = window.location.origin;
const UPDATE_INTERVAL = 2000;
const state = {
    activeView: 'dashboard',
    theme: 'dark',
    charts: {},
    lastAlertKeys: new Set(),
    polling: null
};

function getToday() {
    return new Date().toISOString().split('T')[0];
}

function formatDateLabel(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', { hour: '2-digit', minute: '2-digit' });
}

function formatTimestamp(value) {
    if (!value) return 'No disponible';
    const date = new Date(value);
    return date.toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function setCurrentDateTime() {
    const now = new Date();
    document.getElementById('current-date').textContent = now.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    document.getElementById('current-time').textContent = now.toLocaleTimeString('es-ES');
}

function applyTheme(theme) {
    state.theme = theme;
    document.body.classList.toggle('light-theme', theme === 'light');
    document.getElementById('theme-label').textContent = theme === 'light' ? 'Modo Claro' : 'Modo Oscuro';
    document.getElementById('theme-toggle').querySelector('i').className = theme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
    localStorage.setItem('energy-theme', theme);
}

function toggleTheme() {
    applyTheme(state.theme === 'dark' ? 'light' : 'dark');
}

function setActiveView(view) {
    state.activeView = view;
    document.querySelectorAll('.sidebar-item').forEach(button => button.classList.toggle('active', button.dataset.view === view));
    document.querySelectorAll('.view').forEach(section => section.classList.toggle('hidden', section.id !== `view-${view}`));
}

function buildSeverityBadge(severity) {
    const level = (severity || 'CRITICA').toUpperCase();
    const classes = level === 'ALTA' || level === 'CRITICA' ? 'badge-alert badge-high' : level === 'MEDIA' ? 'badge-alert badge-medium' : 'badge-alert badge-low';
    return `<span class="${classes}">${level}</span>`;
}

function showToast(title, message) {
    const toast = document.getElementById('toast');
    document.getElementById('toast-title').textContent = title;
    document.getElementById('toast-text').textContent = message;
    toast.classList.add('visible');
    setTimeout(() => toast.classList.remove('visible'), 5000);
}

function initCharts() {
    const ctxLine = document.getElementById('lineChart').getContext('2d');
    const ctxAlert = document.getElementById('lineAlertChart').getContext('2d');
    const ctxBarZone = document.getElementById('barZoneChart').getContext('2d');
    const ctxTrend = document.getElementById('trendChart').getContext('2d');
    const ctxDoughnut = document.getElementById('doughnutZoneChart').getContext('2d');

    state.charts.line = new Chart(ctxLine, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Consumo kWh', data: [], borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.15)', tension: 0.35, fill: true, pointRadius: 3 }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.12)' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.12)' }, beginAtZero: true } }, plugins: { legend: { labels: { color: '#cbd5e1' } } } }
    });

    state.charts.alertLine = new Chart(ctxAlert, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Alertas totales', data: [], borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.18)', tension: 0.35, fill: true, pointRadius: 3 }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.12)' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.12)' }, beginAtZero: true } }, plugins: { legend: { labels: { color: '#cbd5e1' } } } }
    });

    state.charts.zoneBar = new Chart(ctxBarZone, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'Zona kWh', data: [], backgroundColor: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'], borderRadius: 14 }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { color: '#94a3b8' }, grid: { display: false } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.12)' }, beginAtZero: true } } }
    });

    state.charts.trend = new Chart(ctxTrend, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Consumo histórico', data: [], borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,0.15)', tension: 0.35, fill: true, pointRadius: 3 }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.12)' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.12)' }, beginAtZero: true } } }
    });

    state.charts.doughnut = new Chart(ctxDoughnut, {
        type: 'doughnut',
        data: { labels: [], datasets: [{ data: [], backgroundColor: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#cbd5e1' } } } }
    });
}

async function fetchJson(path) {
    const response = await fetch(`${API_BASE}${path}`);
    if (!response.ok) throw new Error(`${path} ${response.status}`);
    return response.json();
}

function normalizeAlerts(alertResponse) {
    if (!alertResponse) return [];
    if (Array.isArray(alertResponse)) return alertResponse;
    if (alertResponse.alertas) return alertResponse.alertas;
    return alertResponse;
}

function normalizeRecommendations(recResponse) {
    if (!recResponse) return [];
    if (Array.isArray(recResponse)) return recResponse;
    if (recResponse.recomendaciones) return recResponse.recomendaciones;
    return recResponse;
}

function renderKPIs(summary, alerts, zoneStats) {
    document.getElementById('kpi-total').textContent = `${(summary.consumo_total || 0).toLocaleString('es-ES')} kWh`;
    document.getElementById('kpi-dispositivos').textContent = summary.dispositivos_activos || 0;
    document.getElementById('kpi-alertas').textContent = summary.alertas_hoy || alerts.length || 0;
    document.getElementById('kpi-zona').textContent = zoneStats.criticalZone || '--';
    document.getElementById('kpi-zonas').textContent = zoneStats.activeZones || 0;
    document.getElementById('kpi-altas').textContent = summary.ALTA || 0;
    document.getElementById('kpi-medias').textContent = summary.MEDIA || 0;
    document.getElementById('kpi-criticas').textContent = summary.CRITICA || 0;
}

function computeZoneStats(alerts) {
    const zones = {};
    alerts.forEach(item => {
        const zone = item.zona || 'Desconocida';
        zones[zone] = (zones[zone] || 0) + (Number(item.consumo) || 0);
    });
    const entries = Object.entries(zones).sort((a, b) => b[1] - a[1]);
    return { activeZones: entries.length, criticalZone: entries.length ? entries[0][0] : '--', labels: entries.map(item => item[0]), values: entries.map(item => item[1]) };
}

function renderTopDevices(topDevices) {
    const container = document.getElementById('top-devices');
    if (!topDevices || !topDevices.length) {
        container.innerHTML = '<div class="list-card"><p class="placeholder">No hay datos de dispositivos.</p></div>';
        return;
    }
    const cards = topDevices.map((device, index) => {
        return `<div class="list-card"><div class="kpi-head"><span>#${index + 1}</span><span class="badge-alert badge-low">${device.alertas || 0} alertas</span></div><h5>${device.dispositivo_id}</h5><p>Zona: ${device.zona || 'N/A'}</p><p>Consumo estimado: ${(device.consumo || 0).toFixed(2)} kWh</p></div>`;
    }).join('');
    container.innerHTML = cards;
}

function renderAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    if (!alerts.length) {
        container.innerHTML = '<div class="alert-card"><p class="placeholder">No hay alertas en este momento.</p></div>';
        state.lastAlertKeys.clear();
        return;
    }
    const cards = alerts.map(alert => {
        const severity = (alert.severidad || 'BAJA').toUpperCase();
        const badge = buildSeverityBadge(severity);
        const key = `${alert.dispositivo_id}_${alert.timestamp}_${severity}`;
        if (!state.lastAlertKeys.has(key)) {
            showToast('Nueva alerta registrada', `${alert.dispositivo_id} • ${severity}`);
            state.lastAlertKeys.add(key);
        }
        return `<div class="alert-card"><div class="alert-card-header"><h5>${alert.dispositivo_id}</h5>${badge}</div><div class="alert-card-body"><p><strong>Zona:</strong> ${alert.zona || 'N/A'}</p><p><strong>Consumo:</strong> ${(alert.consumo || 0).toFixed(2)} kWh</p><p><strong>Recomendación:</strong> ${alert.recomendacion || 'No disponible'}</p><p class="kpi-note">${formatTimestamp(alert.timestamp)}</p></div></div>`;
    }).join('');
    container.innerHTML = cards;
}

function renderRecommendations(recommendations) {
    const container = document.getElementById('recommendation-container');
    if (!recommendations.length) {
        container.innerHTML = '<div class="recommendation-card"><p class="placeholder">No hay recomendaciones para hoy.</p></div>';
        return;
    }
    container.innerHTML = recommendations.map(item => {
        const severity = (item.severidad || 'BAJA').toUpperCase();
        const badgeClass = severity === 'ALTA' ? 'badge-alert badge-high' : severity === 'MEDIA' ? 'badge-alert badge-medium' : 'badge-alert badge-low';
        return `<div class="recommendation-card"><div class="kpi-head"><span>${item.dispositivo_id}</span><span class="${badgeClass}">${severity}</span></div><h5>${item.zona || 'Zona desconocida'}</h5><p>${item.recomendacion || 'Recomendación no disponible.'}</p><p class="kpi-note">${formatTimestamp(item.timestamp)}</p></div>`;
    }).join('');
}

function renderHistory(alerts) {
    const table = document.getElementById('history-table');
    if (!alerts.length) {
        table.innerHTML = '<tr><td colspan="7" class="placeholder">Ningún registro histórico disponible.</td></tr>';
        return;
    }
    table.innerHTML = alerts.map((item, idx) => {
        const severityClass = item.severidad === 'ALTA' ? 'badge-alert badge-high' : item.severidad === 'MEDIA' ? 'badge-alert badge-medium' : 'badge-alert badge-low';
        return `<tr><td>${idx + 1}</td><td>${item.dispositivo_id}</td><td>${item.zona}</td><td>${(item.consumo || 0).toFixed(2)} kWh</td><td><span class="${severityClass}">${item.severidad || 'BAJA'}</span></td><td>${item.recomendacion || 'N/A'}</td><td>${formatTimestamp(item.timestamp)}</td></tr>`;
    }).join('');
}

function updateCharts(summary, alertStats, zoneStats, trendData) {
    const now = new Date();
    const label = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    const alertTotal = Object.values(alertStats || {}).reduce((sum, value) => sum + (value || 0), 0);

    const chartLine = state.charts.line;
    chartLine.data.labels.push(label);
    chartLine.data.datasets[0].data.push(summary.consumo_total || 0);
    if (chartLine.data.labels.length > 12) { chartLine.data.labels.shift(); chartLine.data.datasets[0].data.shift(); }
    chartLine.update('none');

    const chartAlert = state.charts.alertLine;
    chartAlert.data.labels.push(label);
    chartAlert.data.datasets[0].data.push(alertTotal);
    if (chartAlert.data.labels.length > 12) { chartAlert.data.labels.shift(); chartAlert.data.datasets[0].data.shift(); }
    chartAlert.update('none');

    state.charts.zoneBar.data.labels = zoneStats.labels.slice(0, 5);
    state.charts.zoneBar.data.datasets[0].data = zoneStats.values.slice(0, 5).map(value => value.toFixed(2));
    state.charts.zoneBar.update('none');

    state.charts.trend.data.labels = trendData.labels;
    state.charts.trend.data.datasets[0].data = trendData.values.map(v => v.toFixed(2));
    state.charts.trend.update('none');

    state.charts.doughnut.data.labels = zoneStats.labels.slice(0, 5);
    state.charts.doughnut.data.datasets[0].data = zoneStats.values.slice(0, 5).map(value => value.toFixed(2));
    state.charts.doughnut.update('none');
}

function buildTrend(alarms) {
    const trend = {};
    alarms.forEach(alert => {
        const date = new Date(alert.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
        trend[date] = (trend[date] || 0) + (Number(alert.consumo) || 0);
    });
    const labels = Object.keys(trend).slice(-12);
    const values = labels.map(label => trend[label]);
    return { labels, values };
}

async function fetchData() {
    const today = getToday();
    try {
        const [summary, alertStats, alertHistory, recs, topDevices] = await Promise.all([
            fetchJson(`/dashboard/${today}`),
            fetchJson(`/estadisticas/alertas/${today}`),
            fetchJson(`/alertas/${today}`),
            fetchJson(`/recomendaciones/${today}`),
            fetchJson(`/estadisticas/top-dispositivos/${today}`)
        ]);

        console.log('summary', summary, 'alertStats', alertStats, 'alertHistory', alertHistory, 'recs', recs, 'topDevices', topDevices);

        const alerts = normalizeAlerts(alertHistory);
        const recommendations = normalizeRecommendations(recs);
        const topList = topDevices.dispositivos || [];
        const zoneStats = computeZoneStats(alerts);
        const summaryWithSeverity = { ...summary, ...(alertStats || {}) };
        const trendData = buildTrend(alerts);

        renderKPIs(summaryWithSeverity, alerts, zoneStats);
        renderTopDevices(topList.map((item) => ({ ...item, consumo: item.consumo || 0 })));
        renderAlerts(alerts);
        renderRecommendations(recommendations);
        renderHistory(alerts);
        updateCharts(summary, alertStats, zoneStats, trendData);
    } catch (error) {
        console.error('Error cargando datos:', error);
    }
}

function startPolling() {
    fetchData();
    if (state.polling) clearInterval(state.polling);
    state.polling = setInterval(fetchData, UPDATE_INTERVAL);
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('energy-theme') || 'dark';
    applyTheme(savedTheme);
    document.querySelectorAll('.sidebar-item').forEach(button => button.addEventListener('click', () => setActiveView(button.dataset.view)));
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    document.getElementById('toast-close').addEventListener('click', () => document.getElementById('toast').classList.remove('visible'));
    setActiveView('dashboard');
    setCurrentDateTime();
    setInterval(setCurrentDateTime, 1000);
    initCharts();
    startPolling();
});
