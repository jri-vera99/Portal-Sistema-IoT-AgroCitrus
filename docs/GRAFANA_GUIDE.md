# Guía de Configuración: Grafana para IoT Agrícola

## 📋 Objetivo

Grafana proporciona visualización avanzada y dashboards interactivos para los datos de sensores almacenados en InfluxDB.

## 📦 Instalación (Raspberry Pi)

### Método 1: APT Repository (Recomendado)

```bash
# Instalar dependencias
sudo apt-get install -y software-properties-common

# Agregar repositorio de Grafana
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Instalar Grafana
sudo apt-get update
sudo apt-get install grafana

# Habilitar inicio automático
sudo systemctl enable grafana-server

# Iniciar Grafana
sudo systemctl start grafana-server

# Verificar estado
sudo systemctl status grafana-server
```

### Método 2: Docker (Alternativo)

```bash
docker run -d \
  --name=grafana \
  -p 3001:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana-oss
```

## 🔑 Acceso Inicial

- **URL**: http://localhost:3001
- **Usuario por defecto**: admin
- **Contraseña por defecto**: admin

**IMPORTANTE**: Cambiar la contraseña en el primer inicio.

## 🔌 Configuración de InfluxDB como Data Source

### Paso 1: Añadir Data Source

1. Ir a **Configuration** → **Data Sources**
2. Click en **Add data source**
3. Seleccionar **InfluxDB**

### Paso 2: Configuración

#### Para InfluxDB 2.x (Flux)

```
Name: InfluxDB-CitrusSensors
Query Language: Flux

HTTP:
  URL: http://localhost:8086
  Access: Server (default)

InfluxDB Details:
  Organization: citrus_org
  Token: [Tu token de InfluxDB]
  Default Bucket: citrus_sensors
```

#### Para InfluxDB 1.x (InfluxQL)

```
Name: InfluxDB-CitrusSensors
Query Language: InfluxQL

HTTP:
  URL: http://localhost:8086
  Access: Server (default)

InfluxDB Details:
  Database: citrus_sensors
  User: [opcional]
  Password: [opcional]
```

### Paso 3: Test & Save

Click en **Save & Test**. Debe mostrar: "Data source is working"

## 📊 Creación de Dashboards

### Dashboard 1: Vista General del Cultivo

#### Panel 1: Temperatura en Tiempo Real

**Query (Flux)**:
```flux
from(bucket: "citrus_sensors")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r.sensor_type == "temperature")
  |> filter(fn: (r) => r._field == "value")
  |> aggregateWindow(every: 5m, fn: mean)
```

**Configuración**:
- **Visualization**: Time series
- **Title**: Temperatura del Cultivo
- **Unit**: Celsius (°C)
- **Color scheme**: Green-Yellow-Red
- **Thresholds**:
  - < 20°C: Blue
  - 20-28°C: Green
  - 28-32°C: Yellow
  - > 32°C: Red

#### Panel 2: Humedad del Suelo

**Query (Flux)**:
```flux
from(bucket: "citrus_sensors")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r.sensor_type == "soil_moisture")
  |> filter(fn: (r) => r._field == "value")
  |> aggregateWindow(every: 5m, fn: mean)
```

**Configuración**:
- **Visualization**: Gauge
- **Title**: Humedad del Suelo
- **Unit**: Percent (0-100)
- **Thresholds**:
  - < 35%: Red (Crítico)
  - 35-40%: Yellow (Bajo)
  - 40-70%: Green (Óptimo)
  - > 70%: Blue (Alto)

#### Panel 3: Humedad del Aire

**Query (Flux)**:
```flux
from(bucket: "citrus_sensors")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r.sensor_type == "air_humidity")
  |> filter(fn: (r) => r._field == "value")
  |> last()
```

**Configuración**:
- **Visualization**: Stat
- **Title**: Humedad del Aire Actual
- **Unit**: Percent (0-100)
- **Color mode**: Value

#### Panel 4: Luminosidad

**Query (Flux)**:
```flux
from(bucket: "citrus_sensors")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r.sensor_type == "luminosity")
  |> filter(fn: (r) => r._field == "value")
  |> aggregateWindow(every: 1h, fn: mean)
```

**Configuración**:
- **Visualization**: Bar chart
- **Title**: Luminosidad (24h)
- **Unit**: Lux
- **Color**: Yellow gradient

### Dashboard 2: Análisis Histórico

#### Panel 1: Comparación Semanal de Temperatura

**Query (Flux)**:
```flux
from(bucket: "citrus_sensors")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r.sensor_type == "temperature")
  |> filter(fn: (r) => r._field == "value")
  |> aggregateWindow(every: 1h, fn: mean)
  |> group(columns: ["node_id"])
```

**Configuración**:
- **Visualization**: Time series
- **Legend**: Show
- **Time range**: Last 7 days

#### Panel 2: Estadísticas Diarias

**Query (Flux)**:
```flux
import "contrib/tomhollingworth/events"

from(bucket: "citrus_sensors")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "value")
  |> group(columns: ["sensor_type"])
  |> aggregateWindow(every: 24h, fn: mean)
```

**Configuración**:
- **Visualization**: Table
- **Columns**: Sensor Type, Min, Max, Mean

### Dashboard 3: Mapa de Sensores (Avanzado)

#### Panel: Geomap

**Query (Flux)**:
```flux
from(bucket: "citrus_sensors")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "value")
  |> last()
  |> map(fn: (r) => ({ 
      r with 
      lat: float(v: r.latitude),
      lon: float(v: r.longitude)
    }))
```

**Configuración**:
- **Visualization**: Geomap
- **View**: Fit data
- **Location**: Use latitude/longitude fields
- **Marker**: Circle with value-based color

## 🎛️ Variables de Dashboard

### Variable 1: Nodo de Sensor

```
Name: node
Type: Query
Data source: InfluxDB-CitrusSensors

Query (Flux):
import "influxdata/influxdb/schema"

schema.tagValues(
  bucket: "citrus_sensors",
  tag: "node_id"
)
```

### Variable 2: Tipo de Sensor

```
Name: sensor_type
Type: Query
Data source: InfluxDB-CitrusSensors

Query (Flux):
import "influxdata/influxdb/schema"

schema.tagValues(
  bucket: "citrus_sensors",
  tag: "sensor_type"
)
```

### Uso de Variables en Queries

```flux
from(bucket: "citrus_sensors")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r.node_id == "${node}")
  |> filter(fn: (r) => r.sensor_type == "${sensor_type}")
  |> filter(fn: (r) => r._field == "value")
```

## 🔔 Configuración de Alertas

### Alerta 1: Temperatura Alta

1. Ir al panel de Temperatura
2. Click en **Alert** tab
3. **Create Alert Rule**

```
Name: Temperatura Alta - Cultivo de Mandarina

Conditions:
  WHEN avg() OF query(A, 5m, now)
  IS ABOVE 32

Notifications:
  Send to: Email / Webhook
  Message: ¡Alerta! Temperatura del cultivo supera 32°C

Evaluation:
  Evaluate every: 1m
  For: 5m
```

### Alerta 2: Humedad Crítica del Suelo

```
Name: Humedad Crítica del Suelo

Conditions:
  WHEN avg() OF query(A, 5m, now)
  IS BELOW 35

Notifications:
  Send to: Email / Webhook
  Message: ¡Alerta Crítica! Humedad del suelo por debajo del 35%

Evaluation:
  Evaluate every: 2m
  For: 5m
```

### Configurar Notification Channel

#### Email
```
Type: Email
Name: Alertas IoT
Addresses: tu@email.com
```

#### Webhook (Backend FastAPI)
```
Type: Webhook
Name: Backend API
Url: http://localhost:8001/api/webhooks/grafana
HTTP Method: POST
HTTP Headers:
  Content-Type: application/json
```

## 🎨 Personalización

### Tema Personalizado

Editar `/etc/grafana/grafana.ini`:

```ini
[server]
protocol = http
http_port = 3001
domain = localhost
root_url = http://localhost:3001

[security]
admin_user = admin
admin_password = tu-password-segura

[auth.anonymous]
enabled = false

[dashboards]
default_home_dashboard_path = /var/lib/grafana/dashboards/citrus-overview.json
```

### Logo Personalizado

```bash
sudo cp tu-logo.png /usr/share/grafana/public/img/grafana_icon.svg
sudo systemctl restart grafana-server
```

## 📥 Exportar/Importar Dashboards

### Exportar Dashboard

1. Abrir dashboard
2. Click en **Share** (icono compartir)
3. Tab **Export**
4. **Save to file**

### Importar Dashboard

1. Ir a **Dashboards** → **Browse**
2. Click **Import**
3. Upload JSON file o pegar JSON
4. Seleccionar data source
5. **Import**

## 🔗 Integración con Frontend React

### Embeber Dashboard en iframe

```jsx
// En tu componente React
<iframe
  src="http://localhost:3001/d/citrus-overview?orgId=1&theme=light&kiosk"
  width="100%"
  height="600px"
  frameBorder="0"
  title="Dashboard IoT"
></iframe>
```

### Parámetros de URL

- `theme=light` o `theme=dark`: Tema
- `kiosk`: Modo quiosco (oculta menús)
- `from=now-6h&to=now`: Rango de tiempo
- `var-node=node_01`: Establecer variable

### Autenticación

Para embeber con autenticación, configurar en `grafana.ini`:

```ini
[auth.anonymous]
enabled = true
org_name = CitrusIoT
org_role = Viewer
```

## 🛠️ Plugins Recomendados

### Instalar Plugins

```bash
# Clock Panel
sudo grafana-cli plugins install grafana-clock-panel

# Worldmap Panel
sudo grafana-cli plugins install grafana-worldmap-panel

# Pie Chart
sudo grafana-cli plugins install grafana-piechart-panel

# Reiniciar Grafana
sudo systemctl restart grafana-server
```

## 📊 Queries Útiles

### Último Valor de Todos los Sensores

```flux
from(bucket: "citrus_sensors")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "value")
  |> last()
  |> group(columns: ["node_id", "sensor_type"])
```

### Promedio Diario por Tipo de Sensor

```flux
from(bucket: "citrus_sensors")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "value")
  |> aggregateWindow(every: 1d, fn: mean)
  |> group(columns: ["sensor_type"])
```

### Detectar Valores Anómalos

```flux
from(bucket: "citrus_sensors")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r.sensor_type == "temperature")
  |> filter(fn: (r) => r._field == "value")
  |> filter(fn: (r) => r._value > 35 or r._value < 15)
```

## 🔧 Troubleshooting

### Grafana no inicia

```bash
sudo systemctl status grafana-server
sudo journalctl -u grafana-server -f
```

### Data source no conecta

```bash
# Verificar InfluxDB
curl http://localhost:8086/ping

# Verificar token
influx auth list
```

### Dashboard no muestra datos

1. Verificar data source configurado
2. Revisar query en Query Inspector
3. Verificar rango de tiempo
4. Confirmar que hay datos en InfluxDB:

```bash
influx query 'from(bucket:"citrus_sensors") |> range(start: -1h) |> limit(n:10)'
```

## 📚 Recursos

- [Grafana Documentation](https://grafana.com/docs/)
- [InfluxDB Flux](https://docs.influxdata.com/flux/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

---

**Próximo Paso**: Configurar alertas y notificaciones para monitoreo proactivo del cultivo.