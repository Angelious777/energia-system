// ========================================
// ENERGY DASHBOARD v2.0 - MODERN APP
// ========================================

class EnergyDashboard {
    constructor() {
        const origin = window.location.origin;
        this.API_BASE = origin && origin !== 'null' && origin !== 'file://' ? origin : 'http://127.0.0.1:5000';
        this.UPDATE_INTERVAL = 2000;
        this.state = {
            activeView: 'dashboard',
            theme: 'dark',
            charts: {},
            alerts: [],
            devices: [],
            lastUpdate: null
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTheme();
        this.updateTime();
        this.initCharts();
        this.loadData();
        this.startAutoUpdate();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.addEventListener('click', () => this.setActiveView(item.dataset.view));
        });

        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Toast close
        document.getElementById('toastClose')?.addEventListener('click', () => {
            this.hideToast();
        });
    }

    loadTheme() {
        const saved = localStorage.getItem('energy-theme') || 'dark';
        document.body.classList.toggle('light-theme', saved === 'light');
        this.state.theme = saved;
        this.updateThemeUI();
    }

    toggleTheme() {
        this.state.theme = this.state.theme === 'dark' ? 'light' : 'dark';
        document.body.classList.toggle('light-theme', this.state.theme === 'light');
        localStorage.setItem('energy-theme', this.state.theme);
        this.updateThemeUI();
    }

    updateThemeUI() {
        const icon = document.querySelector('#theme-toggle i');
        const label = document.querySelector('#theme-toggle span');
        
        if (this.state.theme === 'light') {
            icon.className = 'fas fa-sun';
            label.textContent = 'Modo Claro';
        } else {
            icon.className = 'fas fa-moon';
            label.textContent = 'Modo Oscuro';
        }
    }

    setActiveView(view) {
        this.state.activeView = view;
        
        // Update sidebar
        document.querySelectorAll('.sidebar-item').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });
        
        // Update views
        document.querySelectorAll('.view').forEach(section => {
            section.classList.toggle('active', section.id === `view-${view}`);
            section.classList.toggle('hidden', section.id !== `view-${view}`);
        });
        
        // Update page title
        const titles = {
            dashboard: 'Dashboard Principal',
            consumo: 'Análisis de Consumo',
            alertas: 'Alertas en Tiempo Real',
            recomendaciones: 'Recomendaciones IA',
            historico: 'Historial Completo'
        };
        
        document.getElementById('page-title').textContent = `Monitoreo Energético - ${titles[view] || 'La Paz'}`;
    }

    updateTime() {
        const now = new Date();
        document.getElementById('current-date').textContent = 
            now.toLocaleDateString('es-ES', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
        document.getElementById('current-time').textContent = 
            now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    }

    async loadData() {
        try {
            this.showLoading();
            
            const today = new Date().toISOString().split('T')[0];
            console.log('API base:', this.API_BASE);
            console.log('Fetching endpoints:', [
                `${this.API_BASE}/dashboard/${today}`,
                `${this.API_BASE}/alertas/${today}`,
                `${this.API_BASE}/alertas/recientes`,
                `${this.API_BASE}/dispositivos/${today}`,
                `${this.API_BASE}/zonas/${today}`,
                `${this.API_BASE}/estadisticas/alertas/${today}`,
                `${this.API_BASE}/recomendaciones/${today}`
            ]);

            const [summary, historyAlerts, realtimeAlertsRaw, devices, zones, severityStats, recommendations] = await Promise.all([
                this.fetchJson(`/dashboard/${today}`),
                this.fetchJson(`/alertas/${today}`),
                this.fetchJson(`/alertas/recientes`),
                this.fetchJson(`/dispositivos/${today}`),
                this.fetchJson(`/zonas/${today}`),
                this.fetchJson(`/estadisticas/alertas/${today}`),
                this.fetchJson(`/recomendaciones/${today}`)
            ]);

            const realtimeAlerts = realtimeAlertsRaw?.alertas || realtimeAlertsRaw || [];
            const recommendationList = recommendations?.recomendaciones || recommendations || [];

            this.state.alerts = historyAlerts;
            this.state.devices = devices;
            
            this.updateUI(summary, realtimeAlerts, devices, zones, severityStats);
            this.updateCharts(summary, zones);
            this.updateSeverityChart(severityStats);
            this.updateZoneChart(zones);
            this.updateTrendChart(zones);
            this.updateRealTimeAlerts(realtimeAlerts);
            this.updateRecommendations(recommendationList);
            this.updateTopDevices(devices);
            this.updateHistory(historyAlerts);
            
            document.getElementById('sidebar-alerts').textContent = realtimeAlerts.length;
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Error de conexión. Reintentando...');
        } finally {
            this.hideLoading();
        }
    }

    updateUI(summary, alerts, devices, zones, severityStats) {
        // Update KPIs
        document.getElementById('kpi-total').innerHTML = 
            `${(summary.consumo_total || 0).toLocaleString()} <span>kWh</span>`;
        document.getElementById('kpi-dispositivos').textContent = devices.length;
        document.getElementById('kpi-alertas').textContent = alerts.length;
        document.getElementById('kpi-zona').textContent = zones.labels?.[0] || 'N/A';
        
        // Update alert status
        const alertStatus = document.getElementById('alert-status');
        if (alerts.length === 0) {
            alertStatus.textContent = 'Normal';
            alertStatus.parentElement.className = 'kpi-status online';
        } else {
            alertStatus.textContent = alerts.length > 5 ? 'Crítico' : 'Advertencia';
            alertStatus.parentElement.className = `kpi-status ${alerts.length > 5 ? 'critical' : 'warning'}`;
        }
        
        // New alerts toast
        alerts.forEach(alert => {
            if (!this.state.lastAlerts?.includes(alert.alerta_id)) {
                this.showToast('🔔 Nueva Alerta', `${alert.dispositivo_id} - ${alert.severidad}`);
            }
        });
        this.state.lastAlerts = alerts.map(alert => alert.alerta_id);

        // Update severity badges
        const severityBadge = document.getElementById('kpi-alertas');
        if (severityStats.ALTA + severityStats.CRITICA > 5) {
            severityBadge.parentElement.className = 'kpi-status critical';
        } else if (severityStats.MEDIA > 0) {
            severityBadge.parentElement.className = 'kpi-status warning';
        }
    }

    initCharts() {
        // Main Chart
        const mainCtx = document.getElementById('mainChart')?.getContext('2d');
        if (mainCtx) {
            this.state.charts.main = new Chart(mainCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Consumo (kWh)',
                        data: [],
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: 'rgba(255,255,255,0.8)', padding: 30 }
                        }
                    },
                    scales: {
                        x: { 
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            ticks: { color: 'rgba(255,255,255,0.6)' }
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            ticks: { color: 'rgba(255,255,255,0.6)' }
                        }
                    },
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuart'
                    }
                }
            });
        }

        // Zone Chart
        const zoneCtx = document.getElementById('zoneChart')?.getContext('2d');
        if (zoneCtx) {
            this.state.charts.zone = new Chart(zoneCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: 'rgba(255,255,255,0.8)' }
                        }
                    }
                }
            });
        }

        const alertCtx = document.getElementById('alertChart')?.getContext('2d');
        if (alertCtx) {
            this.state.charts.alert = new Chart(alertCtx, {
                type: 'bar',
                data: {
                    labels: ['BAJA', 'MEDIA', 'ALTA', 'CRITICA'],
                    datasets: [{
                        label: 'Alertas',
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#14b8a6', '#f59e0b', '#ef4444', '#c026d3']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { ticks: { color: 'rgba(255,255,255,0.8)' } },
                        y: { ticks: { color: 'rgba(255,255,255,0.8)' }, beginAtZero: true }
                    }
                }
            });
        }

        const trendCtx = document.getElementById('trendChart')?.getContext('2d');
        if (trendCtx) {
            this.state.charts.trend = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Tendencia de consumo',
                        data: [],
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34,197,94,0.2)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: 'rgba(255,255,255,0.8)' } }
                    },
                    scales: {
                        x: { ticks: { color: 'rgba(255,255,255,0.8)' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        y: { ticks: { color: 'rgba(255,255,255,0.8)' }, grid: { color: 'rgba(255,255,255,0.1)' }, beginAtZero: true }
                    }
                }
            });
        }

        const doughnutCtx = document.getElementById('zoneDoughnut')?.getContext('2d');
        if (doughnutCtx) {
            this.state.charts.zoneDoughnut = new Chart(doughnutCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: 'rgba(255,255,255,0.8)' } }
                    }
                }
            });
        }
    }

    updateCharts(summary, zones) {
        const mainChart = this.state.charts.main;
        if (mainChart) {
            const now = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            mainChart.data.labels.push(now);
            mainChart.data.datasets[0].data.push(summary.consumo_total || 0);
            
            if (mainChart.data.labels.length > 20) {
                mainChart.data.labels.shift();
                mainChart.data.datasets[0].data.shift();
            }
            
            mainChart.update('quiet');
        }
    }

    updateZoneChart(zones) {
        const chart = this.state.charts.zone;
        const doughnut = this.state.charts.zoneDoughnut;
        if (!zones) return;

        const labels = zones.labels || [];
        const values = zones.values || [];

        if (chart) {
            chart.data.labels = labels;
            chart.data.datasets[0].data = values;
            chart.update('quiet');
        }
        if (doughnut) {
            doughnut.data.labels = labels;
            doughnut.data.datasets[0].data = values;
            doughnut.update('quiet');
        }
    }

    updateSeverityChart(severityStats) {
        const chart = this.state.charts.alert;
        if (!chart || !severityStats) return;
        chart.data.labels = ['BAJA', 'MEDIA', 'ALTA', 'CRITICA'];
        chart.data.datasets[0].data = [0, severityStats.MEDIA || 0, severityStats.ALTA || 0, severityStats.CRITICA || 0];
        chart.update('quiet');
    }

    updateTrendChart(zones) {
        const chart = this.state.charts.trend;
        if (!chart || !zones?.tendencia) return;
        chart.data.labels = zones.tendencia.labels || [];
        chart.data.datasets[0].data = zones.tendencia.values || [];
        chart.update('quiet');
    }

    updateTopDevices(devices) {
        const container = document.getElementById('topDevicesList');
        if (!container) return;
        if (!devices || devices.length === 0) {
            container.innerHTML = '<div class="empty-card">No hay dispositivos críticos.</div>';
            return;
        }
        container.innerHTML = devices.slice(0, 5).map((device, idx) => {
            return `
                <div class="device-card">
                    <div class="device-rank">#${idx + 1}</div>
                    <div>
                        <h4>${device.dispositivo_id}</h4>
                        <p>${device.alertas || 0} alertas</p>
                    </div>
                </div>
            `;
        }).join('');
    }

    updateRealTimeAlerts(alerts) {
        const container = document.getElementById('alertsGrid');
        if (!container) return;
        if (!alerts || alerts.length === 0) {
            container.innerHTML = '<div class="alert-empty">No hay alertas recientes.</div>';
            return;
        }
        container.innerHTML = alerts.slice(0, 8).map(alert => {
            const severityClass = alert.severidad === 'CRITICA' ? 'danger' : alert.severidad === 'ALTA' ? 'warning' : 'info';
            return `
                <div class="alert-card ${severityClass}">
                    <div class="alert-card-header">
                        <h4>${alert.dispositivo_id}</h4>
                        <span>${alert.severidad}</span>
                    </div>
                    <div class="alert-card-body">
                        <p>Zona: ${alert.zona || 'N/A'}</p>
                        <p>Consumo: ${Number(alert.consumo || 0).toFixed(2)} kWh</p>
                        <p>${alert.recomendacion || 'Sin recomendación'}</p>
                        <small>${new Date(alert.timestamp).toLocaleString('es-ES')}</small>
                    </div>
                </div>
            `;
        }).join('');
    }

    updateRecommendations(recommendations) {
        const container = document.getElementById('recommendationsGrid');
        if (!container) return;
        if (!recommendations || recommendations.length === 0) {
            container.innerHTML = '<div class="recommendation-empty">No hay recomendaciones disponibles.</div>';
            return;
        }
        container.innerHTML = recommendations.slice(0, 8).map(item => {
            return `
                <div class="recommendation-card">
                    <h4>${item.dispositivo_id}</h4>
                    <p>Zona: ${item.zona || 'N/A'}</p>
                    <p>${item.recomendacion || 'Monitorear uso'}</p>
                    <small>${new Date(item.timestamp).toLocaleString('es-ES')}</small>
                </div>
            `;
        }).join('');
    }

    updateHistory(alerts) {
        const tbody = document.getElementById('historyTable');
        if (!tbody) return;
        if (!alerts || alerts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No hay eventos históricos.</td></tr>';
            return;
        }
        tbody.innerHTML = alerts.map((item, idx) => {
            const severityClass = item.severidad === 'CRITICA' ? 'critical' : item.severidad === 'ALTA' ? 'warning' : 'normal';
            return `
                <tr>
                    <td>${idx + 1}</td>
                    <td>${item.dispositivo_id}</td>
                    <td>${item.zona}</td>
                    <td>${Number(item.consumo || 0).toFixed(2)} kWh</td>
                    <td><span class="severity ${severityClass}">${item.severidad}</span></td>
                    <td>${item.recomendacion || 'N/A'}</td>
                    <td>${new Date(item.timestamp).toLocaleString('es-ES')}</td>
                </tr>
            `;
        }).join('');
    }

    async fetchJson(endpoint) {
        let url = `${this.API_BASE}${endpoint}`;
        if (!url.startsWith('http')) {
            url = `http://127.0.0.1:5000${endpoint}`;
        }
        console.log('Fetching URL:', url);
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        } catch (error) {
            const fallbackUrl = `http://127.0.0.1:5000${endpoint}`;
            if (url !== fallbackUrl) {
                console.warn('Fetch failed, retrying with fallback URL:', fallbackUrl);
                const response = await fetch(fallbackUrl);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            }
            throw error;
        }
    }

    showToast(title, message) {
        document.getElementById('toastTitle').textContent = title;
        document.getElementById('toastMessage').textContent = message;
        document.getElementById('mainToast').classList.add('show');
        
        setTimeout(() => {
            document.getElementById('mainToast').classList.remove('show');
        }, 5000);
    }

    showLoading() {
        document.querySelector('.sidebar-status span').textContent = 'Actualizando...';
        document.querySelector('.sidebar-status i').classList.add('fa-spin');
    }

    hideLoading() {
        document.querySelector('.sidebar-status span').textContent = 'Listo';
        document.querySelector('.sidebar-status i').classList.remove('fa-spin');
        this.state.lastUpdate = new Date();
    }

    startAutoUpdate() {
        setInterval(() => this.loadData(), this.UPDATE_INTERVAL);
        setInterval(() => this.updateTime(), 1000);
    }

    showError(message) {
        this.showToast('⚠️ Error', message);
    }
}

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    new EnergyDashboard();
    
    // Hide loading screen after 2s
    setTimeout(() => {
        document.getElementById('loadingScreen').style.opacity = '0';
        setTimeout(() => document.getElementById('loadingScreen').remove(), 500);
    }, 2000);
});