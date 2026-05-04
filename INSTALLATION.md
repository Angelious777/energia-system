# 🚀 Guía de Instalación y Ejecución del Dashboard

## ⚙️ Requisitos Previos

- Python 3.8+
- pip (Python package manager)
- Navegador moderno (Chrome, Firefox, Safari, Edge)
- Flask 2.x
- Redis y Cassandra (según configuración backend)

## 📦 Instalación

### Paso 1: Verificar Estructura

Asegurar que existan estas carpetas en la raíz del proyecto:
```
templates/
  └── dashboard.html

static/
  ├── css/
  │   └── dashboard.css
  └── js/
      └── dashboard.js
```

### Paso 2: Instalar Dependencias (si es necesario)

```bash
cd c:\Users\VIVI\OneDrive\Documentos\BDIII\PROYECTO\APLICACION\GITHUB\energia-system

# Crear entorno virtual (si no existe)
python -m venv venv

# Activar entorno virtual
venv\Scripts\Activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Configurar Variables de Entorno

Verificar que el archivo `.env` tenga las configuraciones correctas para:
- Redis
- Cassandra
- Puerto Flask (por defecto 5000)

## 🎬 Ejecución

### Opción 1: Ejecución Directa

```bash
# Activar entorno virtual
venv\Scripts\Activate

# Ejecutar Flask
python app.py
```

Salida esperada:
```
WARNING: This is a development server. Do not use it in production.
Press CTRL+C to quit
* Running on http://0.0.0.0:5000
```

### Opción 2: Ejecución con Gunicorn (Producción)

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🌐 Acceder al Dashboard

Una vez el servidor esté ejecutándose, abrir en navegador:

```
http://localhost:5000/
```

### En Red Local

Para acceder desde otro dispositivo en la misma red:

```
http://<IP_LOCAL>:5000/
```

Encontrar IP local:
```powershell
ipconfig
```

## 📊 Verificar Conectividad

### 1. Verificar que Flask está corriendo

```bash
curl http://localhost:5000/
```

Deberá responder con HTML del dashboard.

### 2. Verificar endpoints de API

```bash
# Hoy
$today = (Get-Date).ToString("yyyy-MM-dd")

# Dashboard
curl "http://localhost:5000/dashboard/resumen/$today"

# Alertas
curl "http://localhost:5000/estadisticas/alertas/$today"

# Top dispositivos
curl "http://localhost:5000/estadisticas/top-dispositivos/$today"
```

## 🔍 Troubleshooting

### "Address already in use"

El puerto 5000 ya está en uso. Opciones:

```bash
# Opción 1: Encontrar qué usa el puerto
netstat -ano | findstr :5000

# Opción 2: Usar otro puerto
# Modificar en app.py:
# app.run(debug=True, host='0.0.0.0', port=5001)

# Opción 3: Matar el proceso
taskkill /PID <PID> /F
```

### "No module named 'flask'"

Instalar Flask:
```bash
pip install flask
```

### "No module named 'redis'" o "No module named 'cassandra'"

Instalar las dependencias:
```bash
pip install redis cassandra-driver
```

### Dashboard carga pero no muestra datos

1. **Verificar consola del navegador** (F12 → Console):
   - Buscar errores de CORS
   - Buscar errores de fetch

2. **Verificar que endpoints devuelvan datos**:
   ```powershell
   $date = (Get-Date).ToString("yyyy-MM-dd")
   curl "http://localhost:5000/dashboard/resumen/$date" | ConvertFrom-Json
   ```

3. **Verificar que Redis y Cassandra estén corriendo**:
   - Redis debe estar escuchando en puerto 6379
   - Cassandra debe estar escuchando en puerto 9042

### Gráficos no se muestran

- Verificar que Chart.js se cargue correctamente (revisar Network tab en Dev Tools)
- Verificar que los datos sean numéricos
- Ver consola para errores de JavaScript

### Alertas no aparecen

1. Verificar que el worker esté generando alertas
2. Verificar que `/estadisticas/alertas/<fecha>` devuelva datos
3. Revisar logs de Flask

## 📈 Desarrollo y Debugging

### Activar Debug Mode en Flask

En `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Logs de Aplicación

```bash
# Ver logs en tiempo real
Get-Content logs/* -Tail 50 -Wait
```

### Inspeccionar Datos

En JavaScript Console del navegador:
```javascript
// Enviar request manual
fetch('/dashboard/resumen/2026-05-04')
  .then(r => r.json())
  .then(d => console.log(d))
```

## 🔒 Seguridad (Producción)

### Cambios Recomendados

1. **Deshabilitar debug**:
```python
app.run(debug=False)
```

2. **Usar variables de entorno para sensibles**:
```python
import os
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
```

3. **Configurar CORS si es necesario**:
```python
from flask_cors import CORS
CORS(app)
```

4. **Usar HTTPS en producción**:
```python
app.run(ssl_context='adhoc')  # Requiere pyopenssl
```

## 📝 Configuración Avanzada

### Cambiar Puerto

En `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
```

### Cambiar Intervalo de Actualización

En `static/js/dashboard.js`:
```javascript
const REFRESH_INTERVAL = 5000; // 5 segundos en lugar de 2
```

### Personalizar Tema

En `static/css/dashboard.css`:
```css
:root {
    --primary-color: #1e40af;  /* Azul primario */
    --danger-color: #ef4444;    /* Rojo para alertas */
    /* ... más colores ... */
}
```

## 🧪 Testing

### Test Manual

1. Abrir dashboard en navegador
2. Verificar que muestre datos
3. Verificar que gráficos se actualicen cada 2 segundos
4. Generar una alerta (simulador.py o sensor.py)
5. Verificar que aparezca toast notification
6. Verificar que se agregue a lista de alertas

## 🎯 Checklist de Implementación

- ✅ Carpetas `templates/` y `static/` creadas
- ✅ `dashboard.html` en templates/
- ✅ `dashboard.css` en static/css/
- ✅ `dashboard.js` en static/js/
- ✅ `app.py` configurado con rutas de Flask
- ✅ Endpoints de API funcionando
- ✅ Servidor Flask corriendo
- ✅ Dashboard accesible en http://localhost:5000/

## 📞 Contacto y Soporte

Si hay problemas:

1. Revisar consola del navegador (F12)
2. Revisar logs de Flask
3. Revisar logs de Redis/Cassandra
4. Crear issue con detalles del error

---

**Última actualización**: 2026-05-04  
**Versión**: 1.0
