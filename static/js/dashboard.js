// ========================================
// CONFIGURACIÓN GLOBAL
// ========================================
const API_BASE = window.location.origin; // Usar la misma URL base
const REFRESH_INTERVAL = 2000; // 2 segundos

let charts = {};
let lastAlertIds = new Set();

// ========================================
// INICIALIZACIÓN
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard iniciado');
    
    // Actualizar fecha y hora
    updateDateTime();
    setInterval(updateDateTime, 1000);
    
    // Inicializar gráficos
    initCharts();
    
    // Cargar datos iniciales
    loadDashboardData();
    
    // Actualizar datos cada 2 segundos
    setInterval(loadDashboardData, REFRESH_INTERVAL);
});

// ========================================
// ACTUALIZACIÓN DE FECHA Y HORA
// ========================================
function updateDateTime() {
    const now = new Date();
    
    // Formato de fecha
    const dateOptions = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    const dateStr = now.toLocaleDateString('es-ES', dateOptions);
    document.getElementById('current-date').textContent = dateStr;
    
    // Formato de hora
    const timeStr = now.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    document.getElementById('current-time').textContent = timeStr;
}

// ========================================
// CARGA DE DATOS DEL DASHBOARD
// ========================================
async function loadDashboardData() {
    try {
        // Obtener fecha actual (YYYY-MM-DD)
        const today = new Date().toISOString().split('T')[0];
        
        // Realizar fetch paralelos
        const [dashboardData, alertasData, topDispositivos, zonasData] = await Promise.all([
            fetch(`${API_BASE}/dashboard/resumen/${today}`).then(r => r.json()),
            fetch(`${API_BASE}/estadisticas/alertas/${today}`).then(r => r.json()).catch(() => ({})),
            fetch(`${API_BASE}/estadisticas/top-dispositivos/${today}`).then(r => r.json()).catch(() => ({ dispositivos: [] })),
            fetch(`${API_BASE}/estadisticas/zona/CENTRO/${today}`).then(r => r.json()).catch(() => ({}))
        ]);
        
        // Actualizar KPIs
        updateKPIs(dashboardData, alertasData, topDispositivos);
        
        // Actualizar tabla de dispositivos
        updateTopDispositivos(topDispositivos.dispositivos || []);
        
        // Actualizar alertas
        updateAlertas(alertasData.alertas || []);
        
        // Actualizar gráficos
        updateCharts(dashboardData, topDispositivos);
        
    } catch (error) {
        console.error('Error cargando datos del dashboard:', error);
    }
}

// ========================================
// ACTUALIZAR KPIs
// ========================================
function updateKPIs(dashboardData, alertasData, topDispositivos) {
    // Consumo total
    const consumoTotal = dashboardData.total_consumo || 0;
    document.getElementById('kpi-consumo').textContent = 
        `${consumoTotal.toFixed(2)} kWh`;
    
    // Dispositivos activos
    const deviceCount = topDispositivos.dispositivos?.length || 0;
    document.getElementById('kpi-dispositivos').textContent = deviceCount;
    
    // Total de alertas
    const alertCount = alertasData.alertas?.length || 0;
    document.getElementById('kpi-alertas').textContent = alertCount;
    document.getElementById('alert-count').textContent = alertCount;
    
    // Actualizar estado de alertas
    const alertStatus = document.getElementById('kpi-alertas-status');
    if (alertCount === 0) {
        alertStatus.textContent = 'Normal';
        alertStatus.className = 'badge badge-success';
    } else if (alertCount <= 2) {
        alertStatus.textContent = 'Precaución';
        alertStatus.className = 'badge badge-warning';
    } else {
        alertStatus.textContent = 'Crítico';
        alertStatus.className = 'badge badge-danger';
    }
    
    // Zona con mayor consumo (obtener del primer dispositivo del top)
    if (topDispositivos.dispositivos && topDispositivos.dispositivos.length > 0) {
        const maxZone = topDispositivos.dispositivos[0].zona || 'DESCONOCIDA';
        document.getElementById('kpi-zona').textContent = maxZone;
    }
}

// ========================================
// ACTUALIZAR TABLA DE TOP DISPOSITIVOS
// ========================================
function updateTopDispositivos(dispositivos) {
    const tbody = document.getElementById('top-dispositivos-tbody');
    
    if (!dispositivos || dispositivos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Sin datos</td></tr>';
        return;
    }
    
    // Limitar a top 5
    const top5 = dispositivos.slice(0, 5);
    
    tbody.innerHTML = top5.map((device, index) => `
        <tr>
            <td><strong>${index + 1}</strong></td>
            <td>
                <i class="fas fa-microchip me-2"></i>${device.dispositivo_id || 'N/A'}
            </td>
            <td>
                <span class="badge bg-primary">${device.zona || 'N/A'}</span>
            </td>
            <td class="text-end">
                <strong>${(device.consumo || 0).toFixed(2)}</strong>
            </td>
        </tr>
    `).join('');
}

// ========================================
// ACTUALIZAR ALERTAS
// ========================================
function updateAlertas(alertas) {
    const alertsList = document.getElementById('alerts-list');
    
    if (!alertas || alertas.length === 0) {
        alertsList.innerHTML = `
            <div class="alert-item text-center text-muted py-5">
                <i class="fas fa-inbox fa-2x mb-2"></i>
                <p>Sin alertas en este momento</p>
            </div>
        `;
        lastAlertIds.clear();
        return;
    }
    
    // Verificar nuevas alertas
    alertas.forEach(alert => {
        const alertId = `${alert.dispositivo_id}_${alert.timestamp}`;
        
        if (!lastAlertIds.has(alertId)) {
            // Nueva alerta - mostrar toast
            showAlertToast(alert);
            lastAlertIds.add(alertId);
        }
    });
    
    // Limpiar alertas antiguas de la lista
    if (lastAlertIds.size > alertas.length * 2) {
        lastAlertIds.clear();
        alertas.forEach(alert => {
            lastAlertIds.add(`${alert.dispositivo_id}_${alert.timestamp}`);
        });
    }
    
    // Renderizar alertas
    alertsList.innerHTML = alertas.map(alert => {
        const severity = (alert.severidad || 'BAJA').toUpperCase();
        const severityClass = `alert-${severity.toLowerCase()}`;
        const severityBadgeClass = `severity-${severity.toLowerCase()}`;
        
        return `
            <div class="alert-item ${severityClass}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="text-start flex-grow-1">
                        <div class="alert-device-id">
                            <i class="fas fa-exclamation-circle me-2"></i>${alert.dispositivo_id}
                        </div>
                        <div class="alert-text">
                            Consumo: <strong>${(alert.consumo || 0).toFixed(2)} kWh</strong>
                        </div>
                        <div class="alert-text text-muted" style="font-size: 0.85rem;">
                            <i class="fas fa-map-marker-alt me-1"></i>${alert.zona || 'N/A'}
                        </div>
                        ${alert.recomendacion ? `
                            <div class="alert-text" style="font-size: 0.85rem; color: var(--info-color);">
                                💡 ${alert.recomendacion}
                            </div>
                        ` : ''}
                        <span class="alert-severity ${severityBadgeClass}">
                            ${severity}
                        </span>
                    </div>
                    <small class="text-muted ms-2">${formatTime(alert.timestamp)}</small>
                </div>
            </div>
        `;
    }).join('');
}

// ========================================
// MOSTRAR NOTIFICACIÓN TOAST
// ========================================
function showAlertToast(alert) {
    const toastElement = document.getElementById('alert-toast');
    const messageElement = document.getElementById('toast-message');
    
    const severity = (alert.severidad || 'BAJA').toUpperCase();
    const message = `
        <strong>${alert.dispositivo_id}</strong><br>
        Consumo: ${(alert.consumo || 0).toFixed(2)} kWh<br>
        Severidad: <span class="badge badge-danger">${severity}</span>
        ${alert.recomendacion ? `<br>💡 ${alert.recomendacion}` : ''}
    `;
    
    messageElement.innerHTML = message;
    
    // Agregar clase show y quitar hide
    toastElement.classList.remove('hide');
    toastElement.classList.add('show');
    
    // Auto-cerrar después de 6 segundos
    setTimeout(() => {
        toastElement.classList.remove('show');
        toastElement.classList.add('hide');
    }, 6000);
}

// ========================================
// INICIALIZAR GRÁFICOS
// ========================================
function initCharts() {
    // Contexto para gráfico de consumo
    const consumoCtx = document.getElementById('consumo-chart').getContext('2d');
    
    // Contexto para gráfico de zonas
    const zonaCtx = document.getElementById('zona-chart').getContext('2d');
    
    // Gráfico de consumo en tiempo real
    charts.consumo = new Chart(consumoCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Consumo (kWh)',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#f1f5f9',
                        usePointStyle: true,
                        padding: 20
                    }
                },
                filler: {
                    propagate: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                }
            }
        }
    });
    
    // Gráfico de consumo por zona
    charts.zona = new Chart(zonaCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Consumo (kWh)',
                data: [],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(168, 85, 247, 0.8)'
                ],
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#cbd5e1'
                    }
                }
            }
        }
    });
}

// ========================================
// ACTUALIZAR GRÁFICOS
// ========================================
function updateCharts(dashboardData, topDispositivos) {
    // Simular datos de tiempo real para consumo
    if (charts.consumo) {
        const labels = charts.consumo.data.labels;
        const data = charts.consumo.data.datasets[0].data;
        
        // Agregar nuevo punto (simular cada 2 segundos)
        const now = new Date();
        const timeStr = now.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const consumoActual = dashboardData.total_consumo || 0;
        const variacion = Math.sin(Date.now() / 1000) * 10; // Pequeña variación
        const nuevoConsumo = Math.max(0, consumoActual + variacion);
        
        labels.push(timeStr);
        data.push(nuevoConsumo.toFixed(2));
        
        // Mantener últimos 12 puntos
        if (labels.length > 12) {
            labels.shift();
            data.shift();
        }
        
        charts.consumo.update('none');
    }
    
    // Actualizar gráfico de zonas
    if (charts.zona && topDispositivos.dispositivos) {
        const zonas = {};
        
        // Agrupar por zona
        topDispositivos.dispositivos.forEach(device => {
            const zona = device.zona || 'DESCONOCIDA';
            zonas[zona] = (zonas[zona] || 0) + (device.consumo || 0);
        });
        
        const zonasArray = Object.keys(zonas).slice(0, 5);
        const consumosArray = zonasArray.map(zona => zonas[zona]);
        
        charts.zona.data.labels = zonasArray;
        charts.zona.data.datasets[0].data = consumosArray.map(c => c.toFixed(2));
        charts.zona.update('none');
    }
}

// ========================================
// UTILIDADES
// ========================================
function formatTime(timestamp) {
    if (!timestamp) return 'Hace poco';
    
    try {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000);
        
        if (diff < 60) return 'Hace segundos';
        if (diff < 3600) return `Hace ${Math.floor(diff / 60)} min`;
        if (diff < 86400) return `Hace ${Math.floor(diff / 3600)}h`;
        
        return date.toLocaleDateString('es-ES');
    } catch (e) {
        return 'Recientemente';
    }
}

// Manejo de errores global
window.addEventListener('error', (e) => {
    console.error('Error global:', e.error);
});

// Log de estado
console.log('%c Dashboard iniciado correctamente', 'color: #10b981; font-weight: bold; font-size: 14px;');
console.log('%c Actualizando cada 2 segundos', 'color: #3b82f6; font-size: 12px;');
