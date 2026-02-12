# Guía de Integración: Node-RED para IoT Agrícola

## 🎯 Objetivo

Node-RED actúa como el cerebro del procesamiento de datos en el sistema IoT. Recibe datos de los sensores vía MQTT, los valida, genera alertas y los almacena en InfluxDB.

## 📦 Instalación (Raspberry Pi)

```bash
# Instalar Node-RED
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)

# Habilitar inicio automático
sudo systemctl enable nodered.service

# Iniciar Node-RED
sudo systemctl start nodered.service

# Instalar nodos adicionales
cd ~/.node-red
npm install node-red-contrib-influxdb
npm install node-red-contrib-aedes  # MQTT broker
```

## 🔌 Acceso a Node-RED

- **URL**: http://localhost:1880
- **Editor de flujos**: http://localhost:1880/admin

## 🔄 Flujos Principales

### 1. Flujo de Recepción de Sensores

```json
[
  {
    "id": "mqtt_in_sensors",
    "type": "mqtt in",
    "topic": "citrus/sensors/#",
    "broker": "local_mqtt_broker",
    "outputs": 1,
    "wires": [["validate_sensor_data"]]
  },
  {
    "id": "validate_sensor_data",
    "type": "function",
    "name": "Validar Datos",
    "func": "// Validar estructura del mensaje\nconst payload = msg.payload;\n\nif (!payload.node_id || !payload.sensor_type || payload.value === undefined) {\n    node.warn('Mensaje inválido');\n    return null;\n}\n\n// Validar rangos\nconst ranges = {\n    temperature: [-10, 50],\n    air_humidity: [0, 100],\n    soil_moisture: [0, 100],\n    luminosity: [0, 100000]\n};\n\nconst range = ranges[payload.sensor_type];\nif (range && (payload.value < range[0] || payload.value > range[1])) {\n    node.warn('Valor fuera de rango');\n    return null;\n}\n\nreturn msg;",
    "outputs": 1,
    "wires": [["check_alerts", "write_influxdb"]]
  }
]
```

### 2. Flujo de Alertas

```javascript
// Función: Verificar Alertas
const payload = msg.payload;
const alerts = [];

// Temperatura
if (payload.sensor_type === 'temperature') {
    if (payload.value > 32) {
        alerts.push({
            type: 'high_temperature',
            severity: 'critical',
            message: `Temperatura crítica: ${payload.value}°C`,
            sensor_id: payload.node_id,
            value: payload.value,
            threshold: 32
        });
    } else if (payload.value < 18) {
        alerts.push({
            type: 'low_temperature',
            severity: 'medium',
            message: `Temperatura baja: ${payload.value}°C`,
            sensor_id: payload.node_id,
            value: payload.value,
            threshold: 18
        });
    }
}

// Humedad del suelo
if (payload.sensor_type === 'soil_moisture') {
    if (payload.value < 35) {
        alerts.push({
            type: 'low_soil_moisture',
            severity: 'critical',
            message: `Humedad crítica del suelo: ${payload.value}%`,
            sensor_id: payload.node_id,
            value: payload.value,
            threshold: 35
        });
    } else if (payload.value > 75) {
        alerts.push({
            type: 'high_soil_moisture',
            severity: 'medium',
            message: `Humedad alta del suelo: ${payload.value}%`,
            sensor_id: payload.node_id,
            value: payload.value,
            threshold: 75
        });
    }
}

// Humedad del aire
if (payload.sensor_type === 'air_humidity') {
    if (payload.value < 55) {
        alerts.push({
            type: 'low_air_humidity',
            severity: 'low',
            message: `Humedad baja del aire: ${payload.value}%`,
            sensor_id: payload.node_id,
            value: payload.value,
            threshold: 55
        });
    }
}

// Luminosidad
if (payload.sensor_type === 'luminosity') {
    if (payload.value > 55000) {
        alerts.push({
            type: 'high_luminosity',
            severity: 'medium',
            message: `Luminosidad alta: ${payload.value} lux`,
            sensor_id: payload.node_id,
            value: payload.value,
            threshold: 55000
        });
    }
}

// Enviar alertas al backend
if (alerts.length > 0) {
    msg.payload = alerts;
    return msg;
}

return null;
```

### 3. Flujo de Escritura a InfluxDB

```json
[
  {
    "id": "write_influxdb",
    "type": "influxdb out",
    "influxdb": "local_influxdb",
    "name": "Escribir Sensor",
    "measurement": "sensor_reading",
    "precision": "ms",
    "retentionPolicy": "",
    "database": "citrus_sensors",
    "precisionV18FluxV20": "ms",
    "retentionPolicyV18Flux": "",
    "writeType": "point",
    "x": 600,
    "y": 200,
    "wires": []
  },
  {
    "id": "format_influx",
    "type": "function",
    "name": "Formatear para InfluxDB",
    "func": "const payload = msg.payload;\n\nmsg.payload = {\n    measurement: 'sensor_reading',\n    tags: {\n        node_id: payload.node_id,\n        sensor_type: payload.sensor_type\n    },\n    fields: {\n        value: payload.value\n    },\n    timestamp: new Date(payload.timestamp).getTime()\n};\n\nif (payload.location) {\n    msg.payload.tags.latitude = payload.location.lat;\n    msg.payload.tags.longitude = payload.location.lon;\n}\n\nreturn msg;",
    "outputs": 1,
    "wires": [["write_influxdb"]]
  }
]
```

### 4. Flujo de Estado del Robot

```javascript
// MQTT In: citrus/robot/status
// Función: Procesar Estado del Robot

const status = msg.payload;

// Verificar batería baja
if (status.battery_level < 20) {
    msg.alert = {
        type: 'robot_low_battery',
        severity: 'high',
        message: `Batería baja del robot: ${status.battery_level}%`,
        sensor_id: 'robot_01',
        value: status.battery_level,
        threshold: 20
    };
    // Enviar alerta
}

// Verificar zona permitida (ejemplo)
const homePosition = {lat: -12.0464, lon: -77.0428};
const maxDistance = 0.01; // ~1km

const distance = Math.sqrt(
    Math.pow(status.position.lat - homePosition.lat, 2) +
    Math.pow(status.position.lon - homePosition.lon, 2)
);

if (distance > maxDistance) {
    msg.alert = {
        type: 'robot_out_of_zone',
        severity: 'high',
        message: 'Robot fuera de zona permitida',
        sensor_id: 'robot_01'
    };
}

return msg;
```

## 🔔 Configuración de Alertas

### Umbrales de Alertas

| Parámetro | Crítico | Alto | Medio | Bajo |
|-----------|---------|------|-------|------|
| Temperatura | >32°C o <15°C | >30°C o <18°C | >28°C o <20°C | - |
| Humedad Suelo | <30% | <35% | <40% o >75% | - |
| Humedad Aire | <40% | <50% | <55% o >85% | - |
| Luminosidad | >60k lux | >55k lux | <25k lux | <30k lux |
| Batería Robot | <10% | <20% | <30% | - |

### Envío de Alertas al Backend

```javascript
// Nodo HTTP Request
const alert = msg.payload;

msg.url = 'http://localhost:8001/api/alerts/create';
msg.method = 'POST';
msg.headers = {
    'Content-Type': 'application/json'
};
msg.payload = {
    alert_type: alert.type,
    severity: alert.severity,
    message: alert.message,
    sensor_id: alert.sensor_id,
    value: alert.value,
    threshold: alert.threshold
};

return msg;
```

## 📊 Dashboard en Node-RED

Node-RED incluye un dashboard opcional:

```bash
cd ~/.node-red
npm install node-red-dashboard
```

### Configuración de Gráficos

```json
[
  {
    "type": "ui_chart",
    "name": "Temperatura",
    "group": "sensors",
    "order": 1,
    "width": 6,
    "height": 4,
    "label": "Temperatura (°C)",
    "chartType": "line",
    "legend": "false",
    "xformat": "HH:mm",
    "interpolate": "linear",
    "nodata": "Sin datos",
    "dot": false,
    "ymin": "15",
    "ymax": "35"
  }
]
```

## 🔄 Descifrado AES (Opcional)

Si los datos vienen cifrados desde los ESP32:

```javascript
const crypto = require('crypto');

// Clave AES compartida (16 bytes)
const key = Buffer.from('tu-clave-aes-128', 'utf8');
const iv = Buffer.from('tu-vector-init16', 'utf8');

// Descifrar
const decipher = crypto.createDecipheriv('aes-128-cbc', key, iv);
let decrypted = decipher.update(msg.payload, 'hex', 'utf8');
decrypted += decipher.final('utf8');

msg.payload = JSON.parse(decrypted);
return msg;
```

## 🧪 Testing

### Inyectar Datos de Prueba

```javascript
// Nodo Inject configurado para enviar cada 5 segundos
msg.payload = {
    node_id: 'node_01',
    sensor_type: 'temperature',
    value: 25.5 + (Math.random() * 5 - 2.5),
    timestamp: new Date().toISOString()
};
return msg;
```

## 📝 Exportar/Importar Flujos

### Exportar
1. Seleccionar flujo
2. Menu → Export → Clipboard
3. Copiar JSON

### Importar
1. Menu → Import → Clipboard
2. Pegar JSON
3. Deploy

## 🔧 Troubleshooting

### MQTT no conecta
```bash
sudo systemctl status mosquitto
sudo netstat -tulpn | grep 1883
```

### InfluxDB no escribe
```bash
influx ping
influx auth list
```

### Ver logs de Node-RED
```bash
sudo journalctl -u nodered -f
```

## 📚 Recursos

- [Node-RED Docs](https://nodered.org/docs/)
- [Node-RED IoT](https://cookbook.nodered.org/#iot)
- [InfluxDB Node](https://flows.nodered.org/node/node-red-contrib-influxdb)

---

**Nota**: Esta guía asume Node-RED instalado localmente en Raspberry Pi. Para producción, considerar autenticación y HTTPS.