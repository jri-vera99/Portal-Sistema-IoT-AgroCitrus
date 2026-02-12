# Sistema IoT para Monitoreo de Condiciones Microclimáticas en el Cultivo de Mandarina

##  Descripción del Proyecto

Plataforma IoT profesional para monitoreo en tiempo real de condiciones microclimáticas en cultivos de mandarina (Citrus reticulata), con análisis predictivo basado en IA, control remoto de robot móvil, y visualización avanzada de datos.

##  Arquitectura del Sistema

### Capa de Dispositivos
- **Nodos ESP32 Fijos**: Sensores DS18B20 (temp), SHT31 (humedad), BH1750 (luz), capacitivo (suelo)
- **Robot Móvil ESP32**: Sensores + GPS para monitoreo móvil
- **Comunicación**: WiFi + MQTT con cifrado AES-128

### Capa de Servicios (Raspberry Pi)
- **Mosquitto Broker**: MQTT (puerto 1883)
- **Node-RED**: Procesamiento y reglas de alertas (puerto 1880)
- **InfluxDB**: Base de datos de series temporales (puerto 8086)
- **Backend FastAPI**: API REST + Lógica de negocio (puerto 8001)
- **Frontend React**: Interfaz web (puerto 3000)
- **Grafana**: Dashboards visuales (puerto 3001)

### Capa de Aplicación
- Autenticación JWT
- Dashboards en tiempo real
- Control remoto del robot
- Análisis predictivo con IA (OpenAI GPT-4o-mini)
- Alertas inteligentes

##  Inicio Rápido

### Credenciales por Defecto
```
Usuario: admin
Contraseña: admin123
```

### Acceso a la Plataforma
- **Frontend Web**: https://smartorchard.preview.emergentagent.com
- **API Backend**: https://smartorchard.preview.emergentagent.com/api
- **Grafana**: http://localhost:3001 (acceso local)

##  Endpoints API Principales

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `GET /api/auth/me` - Información del usuario actual

### Sensores
- `GET /api/sensors/latest` - Lecturas más recientes
- `POST /api/sensors/history` - Datos históricos con agregación

### Alertas
- `GET /api/alerts` - Obtener alertas
- `POST /api/alerts/acknowledge` - Reconocer alerta

### Robot
- `GET /api/robot/status` - Estado actual del robot
- `POST /api/robot/control` - Enviar comando al robot
- `GET /api/robot/commands` - Historial de comandos

### Análisis IA
- `POST /api/analysis/predict` - Análisis predictivo con IA

### Sistema
- `GET /api/system/info` - Información del sistema

## Estructura del Proyecto

```
/app/
├── backend/
│   ├── server.py          # Servidor FastAPI principal
│   ├── config.py          # Configuración
│   ├── models.py          # Modelos Pydantic
│   ├── database.py        # SQLite para usuarios/alertas
│   ├── auth.py            # Autenticación JWT
│   ├── influx_client.py   # Cliente InfluxDB
│   ├── mqtt_client.py     # Cliente MQTT
│   ├── ai_analysis.py     # Análisis con IA
│   ├── .env               # Variables de entorno
│   └── requirements.txt   # Dependencias Python
│
├── frontend/
│   ├── src/
│   │   ├── App.js                    # Componente principal
│   │   ├── App.css                   # Estilos globales
│   │   ├── index.css                 # Estilos Tailwind
│   │   ├── api/
│   │   │   └── api.js                # Cliente API axios
│   │   ├── context/
│   │   │   └── AuthContext.js        # Contexto de autenticación
│   │   ├── pages/
│   │   │   ├── Login.js              # Página de login
│   │   │   └── Dashboard.js          # Dashboard principal
│   │   └── components/
│   │       ├── RobotControl.js       # Control del robot
│   │       ├── AlertsPanel.js        # Panel de alertas
│   │       └── AIAnalysisPanel.js    # Panel de análisis IA
│   ├── package.json
│   └── .env
│
└── README.md
```

## Variables de Entorno

### Backend (.env)
```bash
# Base de datos
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"

# JWT
SECRET_KEY="citrus-iot-secret-key-change-in-production-2025"

# MQTT
MQTT_BROKER="localhost"
MQTT_PORT="1883"
MQTT_USERNAME=""
MQTT_PASSWORD=""

# InfluxDB
INFLUXDB_URL="http://localhost:8086"
INFLUXDB_TOKEN=""  # Configurar cuando se instale InfluxDB
INFLUXDB_ORG="citrus_org"
INFLUXDB_BUCKET="citrus_sensors"

# Grafana
GRAFANA_URL="http://localhost:3001"

# IA (Emergent LLM Key)
EMERGENT_LLM_KEY=sk-emergent-c96Ff3e558c1d87F93

# CORS
CORS_ORIGINS="*"
```

### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=https://smartorchard.preview.emergentagent.com
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

## 📡 Configuración MQTT

### Topics
- `citrus/sensors/#` - Datos de sensores
- `citrus/robot/status` - Estado del robot
- `citrus/robot/control` - Comandos al robot
- `citrus/alerts` - Alertas del sistema

### Formato de Mensaje (Sensor)
```json
{
  "node_id": "node_01",
  "sensor_type": "temperature",
  "value": 25.5,
  "location": {"lat": -12.0464, "lon": -77.0428},
  "timestamp": "2025-01-14T17:00:00Z"
}
```

### Formato de Mensaje (Robot)
```json
{
  "status": "moving",
  "battery_level": 85.0,
  "position": {"lat": -12.0464, "lon": -77.0428},
  "speed": 0.5,
  "heading": 45.0,
  "is_moving": true,
  "current_task": "patrol"
}
```

## Esquema de Base de Datos

### SQLite (usuarios y alertas)

#### Tabla: users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'agricultor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);
```

#### Tabla: alerts
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    sensor_id TEXT,
    value REAL,
    threshold REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged INTEGER DEFAULT 0,
    acknowledged_by INTEGER,
    acknowledged_at TIMESTAMP
);
```

#### Tabla: robot_commands
```sql
CREATE TABLE robot_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    command_type TEXT NOT NULL,
    command_data TEXT,
    status TEXT DEFAULT 'sent',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### InfluxDB (series temporales)

#### Measurement: sensor_reading
- **Tags**: node_id, sensor_type, latitude, longitude
- **Fields**: value (float)
- **Timestamp**: Auto-generado
- **Retención**: 1 año (configurable)

## Comandos del Robot

### Manuales
- `move_forward` - Avanzar
- `move_backward` - Retroceder
- `turn_left` - Girar izquierda
- `turn_right` - Girar derecha
- `stop` - Detener

### Automatizados
- `return_home` - Regresar a base
- `start_patrol` - Iniciar patrullaje
- `stop_patrol` - Detener patrullaje
- `go_to_position` - Ir a posición GPS específica

## Análisis con IA

El sistema utiliza OpenAI GPT-4o-mini para:
- Análisis de tendencias de temperatura, humedad, luminosidad
- Predicción de estrés hídrico
- Detección de anomalías
- Generación de recomendaciones
- Evaluación de riesgo del cultivo

### Condiciones Óptimas para Mandarina
- **Temperatura**: 20-30°C (óptimo: 23-28°C)
- **Humedad relativa**: 60-80%
- **Humedad del suelo**: 40-70%
- **Luminosidad**: 30,000-50,000 lux

##  Seguridad

- Autenticación JWT con tokens de 24 horas
- Contraseñas hasheadas con bcrypt
- Comunicación MQTT cifrada con AES-128 (en dispositivos)
- HTTPS para acceso web
- Roles de usuario (admin/agricultor)


## Comandos Útiles

### Backend
```bash
# Reiniciar backend
sudo supervisorctl restart backend

# Ver logs
tail -f /var/log/supervisor/backend.*.log

# Instalar dependencia
cd /app/backend && pip install <paquete> && pip freeze > requirements.txt
```

### Frontend
```bash
# Reiniciar frontend
sudo supervisorctl restart frontend

# Ver logs
tail -f /var/log/supervisor/frontend.*.log

# Instalar dependencia
cd /app/frontend && yarn add <paquete>
```

### Testing
```bash
# Test API login
API_URL="https://smartorchard.preview.emergentagent.com"
curl -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test con token
TOKEN="your-jwt-token"
curl -H "Authorization: Bearer $TOKEN" \
  "$API_URL/api/sensors/latest"
```

## Próximos Pasos

### Para Producción
1. **Instalar y configurar InfluxDB**
   - Crear organización y bucket
   - Generar token de acceso
   - Actualizar .env con credenciales

2. **Instalar y configurar Mosquitto MQTT**
   - Configurar autenticación
   - Habilitar cifrado TLS
   - Actualizar .env con credenciales

3. **Instalar y configurar Grafana**
   - Conectar datasource InfluxDB
   - Importar dashboards
   - Configurar alertas

4. **Configurar Node-RED**
   - Importar flujos
   - Configurar nodos MQTT
   - Configurar nodos InfluxDB
   - Implementar reglas de alertas

5. **Conectar dispositivos ESP32**
   - Flashear firmware con credenciales WiFi/MQTT
   - Calibrar sensores
   - Configurar intervalos de envío

### Mejoras Futuras
- Notificaciones push móviles
- Exportación de reportes PDF
- Integración con sistema de riego automatizado
- Machine Learning para predicción de cosecha
- Aplicación móvil nativa
- Multi-cultivo / Multi-parcela

## Soporte

Este es un proyecto universitario académico. Para preguntas o problemas:
- Revisar logs en `/var/log/supervisor/`
- Verificar estado de servicios: `sudo supervisorctl status`
- Consultar documentación de cada componente

## Licencia

Proyecto académico - Universidad Técnica del Norte - Facultad de Ingeniería en Ciencias Aplicadas -  Carrera de Telecomunicaciones - 2026

---

**Desarrollado por**: Jhojan Rivera
**Curso**: Proyecto Semestral - Seguridad eb Redes y Sistemas de Comunicación Multimedia
**Fecha**: Enero 2025
