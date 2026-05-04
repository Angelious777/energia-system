# 🔌 Dashboard de Monitoreo Energético - La Paz

## 📋 Descripción

Dashboard profesional, moderno y completamente funcional para el sistema de monitoreo energético. Proporciona visibilidad en tiempo real del consumo eléctrico de la ciudad, con alertas dinámicas y análisis detallado.

## ✨ Características Principales

### 1. **KPIs Principales (4 Tarjetas)**
- **Consumo Total**: Consumo acumulado en kWh
- **Dispositivos Activos**: Cantidad de dispositivos conectados
- **Total de Alertas**: Número de alertas generadas
- **Zona con Mayor Consumo**: Zona crítica con mayor consumo

### 2. **Gráficos en Tiempo Real**
- **Gráfico de Línea**: Consumo en tiempo real (actualización cada 2 segundos)
- **Gráfico de Barras**: Consumo por zona (Top 5 zonas)
- Ambos gráficos actualizados automáticamente

### 3. **Tabla de Dispositivos**
- Top 5 dispositivos por consumo
- Información de dispositivo ID, zona y consumo
- Ordenado por mayor consumo

### 4. **Sistema de Alertas Dinámico**
- Lista de alertas recientes
- Colores según severidad:
  - 🔴 **ALTA**: Rojo - Situación crítica
  - 🟡 **MEDIA**: Amarillo - Requiere atención
  - 🟢 **BAJA**: Verde - Normal
- **Toast notifications**: Notificación flotante para nuevas alertas
- Información incluye:
  - Dispositivo
  - Consumo
  - Zona
  - Recomendación
  - Timestamp

### 5. **Actualización Automática**
- Polling cada 2 segundos
- Sin recargar la página
- Actualización suave de datos

### 6. **Diseño Profesional**
- **Dark Mode**: Tema oscuro tipo "sala de control"
- **Responsive**: Se adapta a dispositivos móviles (768px, 480px)
- **Animaciones**: Transiciones suaves (fade-in, slide-in)
- **Iconos**: FontAwesome 6.4.0
- **Bootstrap**: Framework CSS 5.3.0

### 7. **Información Adicional**
- Fecha y hora en vivo (actualización cada segundo)
- Indicador de estado "En vivo"
- Footer con información del sistema

## 📁 Estructura de Archivos

```
templates/
└── dashboard.html          # Estructura HTML del dashboard

static/
├── css/
│   └── dashboard.css       # Estilos oscuros y responsivos
└── js/
    └── dashboard.js        # Lógica JavaScript y fetch
```

## 🚀 Cómo Usar

### 1. **Iniciar el servidor Flask**

```bash
cd c:\Users\VIVI\OneDrive\Documentos\BDIII\PROYECTO\APLICACION\GITHUB\energia-system

# Activar entorno virtual (si es necesario)
venv\Scripts\Activate

# Ejecutar la aplicación
python app.py
```

### 2. **Acceder al Dashboard**

Abrir en el navegador:
```
http://localhost:5000/
```

### 3. **Datos en Vivo**

El dashboard se conecta automáticamente a los siguientes endpoints:

- `GET /dashboard/resumen/<fecha>` - Resumen general del día
- `GET /estadisticas/alertas/<fecha>` - Alertas del día
- `GET /estadisticas/top-dispositivos/<fecha>` - Top 5 dispositivos
- `GET /estadisticas/zona/<zona>/<fecha>` - Consumo por zona

## 🎨 Características de Diseño

### Colores
- **Primario**: Azul (`#3b82f6`)
- **Éxito**: Verde (`#10b981`)
- **Alerta**: Amarillo (`#f59e0b`)
- **Peligro**: Rojo (`#ef4444`)
- **Fondo**: Azul muy oscuro (`#0f172a`)

### Animaciones
- **Fade In**: Aparición suave
- **Slide In**: Entrada desde los lados
- **Hover Effects**: Efectos al pasar mouse
- **Toast**: Notificaciones con animación

### Responsive
- **Escritorio**: Layout completo con 4 columnas de KPI
- **Tablet (768px)**: 2 columnas de KPI, gráficos apilados
- **Móvil (480px)**: 1 columna de KPI, diseño optimizado

## 📊 Integración con Backend

### Endpoints Esperados

El dashboard espera que los endpoints devuelvan datos en este formato:

#### `/dashboard/resumen/<fecha>`
```json
{
  "total_consumo": 1250.75,
  "alertas": [...],
  "zonas": [...],
  "top_dispositivos": [...]
}
```

#### `/estadisticas/alertas/<fecha>`
```json
{
  "alertas": [
    {
      "dispositivo_id": "LPZ_UMSA_AULA_1",
      "zona": "CENTRO",
      "consumo": 250.5,
      "severidad": "ALTA",
      "recomendacion": "Revisar consumo anómalo",
      "timestamp": "2026-05-04T10:00:00"
    }
  ]
}
```

#### `/estadisticas/top-dispositivos/<fecha>`
```json
{
  "dispositivos": [
    {
      "dispositivo_id": "LPZ_UMSA_AULA_1",
      "zona": "CENTRO",
      "consumo": 250.5
    }
  ]
}
```

## 🔧 Configuración

### Intervalo de Actualización

En `static/js/dashboard.js`, línea 6:
```javascript
const REFRESH_INTERVAL = 2000; // Cambiar a milisegundos
```

### API Base

Automáticamente usa `window.location.origin`, por lo que se adapta al servidor actual.

## 📝 Requisitos

- **Backend**: Flask 2.x con endpoints mencionados
- **Frontend**: Navegador moderno (Chrome, Firefox, Safari, Edge)
- **CDNs**: 
  - Bootstrap 5.3.0
  - FontAwesome 6.4.0
  - Chart.js 3.9.1

## ⚙️ Funcionalidad JavaScript

### Funciones Principales

1. **`loadDashboardData()`**: Carga todos los datos del dashboard
2. **`updateKPIs()`**: Actualiza las 4 tarjetas de métricas
3. **`updateTopDispositivos()`**: Actualiza tabla de dispositivos
4. **`updateAlertas()`**: Actualiza lista de alertas
5. **`showAlertToast()`**: Muestra notificación de nueva alerta
6. **`initCharts()`**: Inicializa gráficos con Chart.js
7. **`updateCharts()`**: Actualiza gráficos en tiempo real

### Actualización Automática

```javascript
// Se ejecuta cada 2 segundos
setInterval(loadDashboardData, REFRESH_INTERVAL);
```

## 🎯 UX/UI Highlights

- ✅ Interfaz intuitiva tipo "sala de control"
- ✅ Colores significativos para severidad de alertas
- ✅ Indicador visual "En vivo"
- ✅ Animaciones que no son intrusivas
- ✅ Información clara y jerárquica
- ✅ Responsive y mobile-friendly

## 🚨 Manejo de Alertas

1. **Detección**: Se verifica si hay nuevas alertas
2. **Toast**: Se muestra notificación flotante
3. **Añadido a lista**: Se agrega a la sección de alertas
4. **Auto-cierre**: Toast se cierra automáticamente en 6 segundos
5. **Persistencia**: Las alertas permanecen en la lista hasta que se cargan nuevas

## 📈 Ejemplos de Uso

### Cambiar frecuencia de actualización

```javascript
// En dashboard.js, cambiar REFRESH_INTERVAL
const REFRESH_INTERVAL = 5000; // Actualizar cada 5 segundos
```

### Personalizar colores

```css
/* En dashboard.css, modificar variables CSS */
:root {
    --primary-color: #1e40af;  /* Cambiar azul */
    --danger-color: #ef4444;   /* Cambiar rojo */
}
```

## 🐛 Troubleshooting

### Dashboard no carga
- Verificar que Flask esté corriendo en http://localhost:5000
- Revisar consola del navegador (F12) para errores
- Verificar que endpoints devuelvan datos válidos

### Alertas no aparecen
- Verificar que `/estadisticas/alertas/<fecha>` devuelva datos
- Revisar que `timestamp` tenga formato ISO 8601

### Gráficos no se actualizan
- Verificar que los datos tengan formato numérico
- Revisar consola para errores de Chart.js

## 📞 Soporte

Para problemas o mejoras, revisar:
1. Logs de consola del navegador (F12)
2. Logs del servidor Flask
3. Respuestas de los endpoints en Network tab

---

**Versión**: 1.0  
**Última actualización**: 2026-05-04  
**Autor**: Sistema de Monitoreo Energético
