# 🌐 Gu\u00eda de Arquitectura de Red y Conexión de Dispositivos

## \ud83c\udfaf Arquitectura de Red Dual

Tu sistema tiene una arquitectura de red especial que maneja DOS redes WiFi diferentes:

### **Red Principal** (Router Central)
```
Internet
   |
Router WiFi Central (192.168.1.x)
   |
   ├─── Raspberry Pi 4B (192.168.1.100)
   |      ├─── Mosquitto MQTT (puerto 1883)
   |      ├─── InfluxDB (puerto 8086)
   |      ├─── Node-RED (puerto 1880)
   |      ├─── Grafana (puerto 3001)
   |      ├─── Backend FastAPI (puerto 8001)
   |      └─── Frontend React (puerto 3000)
   |
   ├─── Nodo ESP32 #1 (192.168.1.51)
   ├─── Nodo ESP32 #2 (192.168.1.52)
   ├─── Nodo ESP32 #3 (192.168.1.53)
   └─── Tu computadora / celular
```

### **Red del Robot** (WiFi Direct)
```
Robot ACEBOT QD001
   |
WiFi AP: "ACEBOT-QD001" (192.168.4.x)
   |
   └─── App ACEBOT (celular) o Raspberry Pi
```

---

## \ud83d\udd0c Paso 1: Configurar la Red Principal

### 1.1 Configurar Raspberry Pi

**A. Conectar a tu Router WiFi**

```bash
# En la Raspberry Pi, editar configuraci\u00f3n WiFi
sudo raspi-config

# Navegar a:
# System Options \u2192 Wireless LAN
# SSID: TuWiFi
# Contrase\u00f1a: TuPassword

# O editar manualmente:
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Agregar:
```
network={
    ssid="TuWiFi"
    psk="TuPassword"
}
```

**B. Configurar IP Est\u00e1tica (Recomendado)**

```bash
sudo nano /etc/dhcpcd.conf
```

Agregar al final:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Reiniciar:
```bash
sudo reboot
```

### 1.2 Configurar Nodos ESP32

**En el c\u00f3digo Arduino de cada ESP32:**

```cpp
// Configuraci\u00f3n WiFi
const char* ssid = "TuWiFi";           // El mismo del router
const char* password = "TuPassword";    // La misma contrase\u00f1a

// Configuraci\u00f3n MQTT (IP de la Raspberry Pi)
const char* mqtt_server = "192.168.1.100";  // IP de Raspberry Pi
const int mqtt_port = 1883;
const char* mqtt_user = "citrus_user";      // Si configuraste autenticaci\u00f3n
const char* mqtt_password = "citrus_pass";  // Si configuraste autenticaci\u00f3n

// ID \u00fanico para cada nodo
const char* node_id = "node_01";  // Cambiar para cada ESP32
```

**Flashear el firmware:**
1. Abrir Arduino IDE
2. Cargar el c\u00f3digo del archivo `docs/ESP32_FIRMWARE_GUIDE.md`
3. Seleccionar: Tools \u2192 Board \u2192 ESP32 Dev Module
4. Seleccionar puerto COM correcto
5. Upload

---

## \ud83e\udd16 Paso 2: Integrar el Robot ACEBOT QD001

### Problema de Arquitectura

El robot ACEBOT QD001 crea su propio WiFi y NO se conecta a tu red principal. Esto significa:

\u274c **NO PUEDE**:
- Comunicarse directamente con MQTT
- Estar en la misma red que la Raspberry Pi
- Ser controlado desde la plataforma web sin cambios

\u2705 **SOLUCIONES**:

### **Soluci\u00f3n 1: Adaptador WiFi Dual en Raspberry Pi (Recomendado)**

Compra un adaptador WiFi USB adicional para la Raspberry Pi:

```
Raspberry Pi 4B
  |
  ├─── WiFi Interno (wlan0) \u2192 Conectado a Router (192.168.1.100)
  |      └─── Recibe datos de nodos ESP32 v\u00eda MQTT
  |
  └─── WiFi USB (wlan1) \u2192 Conectado a Robot (192.168.4.2)
         └─── Env\u00eda comandos HTTP al robot
```

**Configuraci\u00f3n:**

```bash
# Ver interfaces WiFi disponibles
ip link show

# Configurar segunda interfaz para el robot
sudo nano /etc/wpa_supplicant/wpa_supplicant-wlan1.conf
```

Agregar:
```
network={
    ssid="ACEBOT-QD001"
    psk="ContrasenadelRobot"
}
```

Habilitar:
```bash
sudo systemctl enable wpa_supplicant@wlan1
sudo systemctl start wpa_supplicant@wlan1
```

### **Soluci\u00f3n 2: Script de Cambio Autom\u00e1tico (Menos Estable)**

Crear un script que alterne entre redes:

```bash
#!/bin/bash
# switch-network.sh

if [ "$1" == "robot" ]; then
    # Desconectar de red principal
    sudo wpa_cli -i wlan0 disconnect
    
    # Conectar a robot
    sudo wpa_cli -i wlan0 add_network
    sudo wpa_cli -i wlan0 set_network 1 ssid \u0022"ACEBOT-QD001"\u0022
    sudo wpa_cli -i wlan0 set_network 1 psk \u0022"ContrasenadelRobot"\u0022
    sudo wpa_cli -i wlan0 enable_network 1
else
    # Reconectar a red principal
    sudo wpa_cli -i wlan0 disconnect
    sudo wpa_cli -i wlan0 enable_network 0
fi
```

**PROBLEMA**: Mientras controlas el robot, pierdes comunicaci\u00f3n con los nodos.

### **Soluci\u00f3n 3: Control Manual Separado (M\u00e1s Simple)**

Mantener el control del robot completamente separado:

1. **App ACEBOT** en tu celular controla el robot directamente
2. **Plataforma Web** solo muestra datos de sensores
3. El panel de control del robot en la web queda como demostraci\u00f3n

**Ventaja**: No necesitas hardware adicional
**Desventaja**: No hay control integrado real

---

## \ud83d\udd27 Paso 3: Configurar Servicios en Raspberry Pi

### 3.1 Instalar Mosquitto MQTT

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients

# Habilitar
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

**Configurar autenticaci\u00f3n (Opcional pero recomendado):**

```bash
# Crear usuario
sudo mosquitto_passwd -c /etc/mosquitto/passwd citrus_user

# Editar configuraci\u00f3n
sudo nano /etc/mosquitto/mosquitto.conf
```

Agregar:
```
allow_anonymous false
password_file /etc/mosquitto/passwd
listener 1883
```

Reiniciar:
```bash
sudo systemctl restart mosquitto
```

### 3.2 Instalar InfluxDB

```bash
# Descargar e instalar
wget https://dl.influxdata.com/influxdb/releases/influxdb2_2.7.5_arm64.deb
sudo dpkg -i influxdb2_2.7.5_arm64.deb

# Iniciar
sudo systemctl enable influxdb
sudo systemctl start influxdb

# Configurar
influx setup --username admin --password citrus2025 --org citrus_org --bucket citrus_sensors --retention 8760h --force
```

**Guardar el token generado** \u2192 Lo necesitar\u00e1s en el Panel de Administraci\u00f3n.

### 3.3 Instalar Node-RED

```bash
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)

# Habilitar
sudo systemctl enable nodered
sudo systemctl start nodered

# Instalar nodos necesarios
cd ~/.node-red
npm install node-red-contrib-influxdb
npm install node-red-dashboard
```

Acceso: `http://192.168.1.100:1880`

### 3.4 Instalar Grafana

```bash
sudo apt install -y software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

sudo apt update
sudo apt install grafana

sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

Acceso: `http://192.168.1.100:3000`
- Usuario: admin
- Contrase\u00f1a: admin (cambiar en primer acceso)

---

## \ud83d\udcca Paso 4: Configurar la Plataforma Web

### 4.1 Desde el Panel de Administraci\u00f3n

1. **Inicia sesi\u00f3n como admin**
   - Usuario: `admin`
   - Contrase\u00f1a: `admin123`

2. **Haz clic en "Admin"** (botón verde en la esquina superior derecha)

3. **Configurar MQTT:**
   - Tab MQTT
   - Broker: `192.168.1.100` (IP de tu Raspberry Pi)
   - Puerto: `1883`
   - Usuario: `citrus_user` (si configuraste autenticaci\u00f3n)
   - Contrase\u00f1a: `citrus_pass`
   - Click "Probar Conexi\u00f3n"
   - Click "Guardar Configuraci\u00f3n"

4. **Configurar InfluxDB:**
   - Tab InfluxDB
   - URL: `http://192.168.1.100:8086`
   - Token: [El token que obtuviste al hacer influx setup]
   - Organizaci\u00f3n: `citrus_org`
   - Bucket: `citrus_sensors`
   - Click "Probar Conexi\u00f3n"
   - Click "Guardar Configuraci\u00f3n"

5. **Agregar Nodos ESP32:**
   - Tab "Nodos ESP32"
   - ID del Nodo: `node_01`
   - Nombre: `Nodo Sector A`
   - Ubicaci\u00f3n: `Parcela Norte`
   - IP Address: `192.168.1.51` (opcional)
   - Click "Agregar Nodo"
   - Repetir para cada nodo
   - Click "Guardar Nodos"

6. **Desactivar Modo Simulaci\u00f3n:**
   - En el panel superior amarillo
   - Activar el switch "Real"
   - Ahora el sistema usar\u00e1 datos reales de los sensores

---

## \ud83d\udce1 Paso 5: Configurar Node-RED

### 5.1 Importar Flujo B\u00e1sico

Accede a Node-RED: `http://192.168.1.100:1880`

1. Men\u00fa (≡) \u2192 Import \u2192 Clipboard
2. Pega este flujo b\u00e1sico:

```json
[
  {
    "id": "mqtt_in",
    "type": "mqtt in",
    "topic": "citrus/sensors/#",
    "broker": "local_broker",
    "outputs": 1,
    "wires": [["process_data"]]
  },
  {
    "id": "process_data",
    "type": "function",
    "name": "Procesar Datos",
    "func": "const data = msg.payload;\\nif (data.node_id && data.sensor_type && data.value !== undefined) {\\n    msg.payload = {\\n        measurement: 'sensor_reading',\\n        tags: {\\n            node_id: data.node_id,\\n            sensor_type: data.sensor_type\\n        },\\n        fields: {\\n            value: data.value\\n        }\\n    };\\n    return msg;\\n}",
    "outputs": 1,
    "wires": [["influx_out"]]
  },
  {
    "id": "influx_out",
    "type": "influxdb out",
    "influxdb": "local_influx",
    "name": "Guardar en InfluxDB",
    "measurement": "sensor_reading",
    "wires": []
  }
]
```

3. Configurar nodos:
   - **mqtt in**: Broker → `localhost:1883`
   - **influxdb out**: Server → `http://localhost:8086`, Token, Org, Bucket

4. Click **Deploy**

---

## \u2705 Verificaci\u00f3n de Funcionamiento

### Test 1: MQTT

Desde la Raspberry Pi:

```bash
# Suscribirse a todos los topics
mosquitto_sub -h localhost -t \"citrus/#\" -v

# En otra terminal, publicar un mensaje de prueba
mosquitto_pub -h localhost -t \"citrus/sensors/test\" -m '{\"node_id\":\"test\",\"sensor_type\":\"temperature\",\"value\":25.5}'
```

Deber\u00edas ver el mensaje en la primera terminal.

### Test 2: ESP32 \u2192 MQTT

Una vez que hayas flasheado un ESP32:

1. Enciende el ESP32
2. Revisa el Monitor Serie (115200 baud)
3. Deber\u00edas ver:
   ```
   Conectando a WiFi...
   WiFi conectado
   IP: 192.168.1.51
   Conectando MQTT...conectado
   Datos enviados
   ```

4. En Raspberry Pi, ejecuta:
   ```bash
   mosquitto_sub -h localhost -t \"citrus/sensors/#\" -v
   ```

5. Deber\u00edas ver los datos de sensores cada 30 segundos

### Test 3: Plataforma Web

1. Accede a la plataforma web
2. Ve al Dashboard
3. Si todo est\u00e1 bien, ver\u00e1s:
   - \u2705 MQTT: Conectado
   - \u2705 InfluxDB: Conectado
   - \ud83d\udfe2 Datos reales de sensores
   - \ud83d\udfe2 Gr\u00e1ficos actualiz\u00e1ndose

---

## \ud83d\udc1b Soluci\u00f3n de Problemas

### ESP32 no conecta a WiFi
- Verifica SSID y contrase\u00f1a
- Aseg\u00farate que el WiFi es 2.4GHz (ESP32 no soporta 5GHz)
- Acerca el ESP32 al router

### ESP32 no publica en MQTT
- Verifica IP de la Raspberry Pi: `ping 192.168.1.100`
- Verifica que Mosquitto est\u00e9 corriendo: `sudo systemctl status mosquitto`
- Revisa firewall: `sudo ufw status`

### Datos no llegan a InfluxDB
- Verifica Node-RED: `http://192.168.1.100:1880`
- Revisa logs: `sudo journalctl -u nodered -f`
- Verifica InfluxDB: `influx ping`

### Plataforma web no muestra datos
- Verifica que desactivaste el modo simulaci\u00f3n
- Revisa la consola del navegador (F12)
- Verifica que MQTT e InfluxDB est\u00e9n conectados

---

## \ud83d\udcdd Resumen de IPs

| Dispositivo | IP | Puerto | Acceso |
|------------|-----|--------|--------|
| Raspberry Pi | 192.168.1.100 | - | SSH: pi@192.168.1.100 |
| Backend API | 192.168.1.100 | 8001 | http://192.168.1.100:8001 |
| Frontend Web | 192.168.1.100 | 3000 | http://192.168.1.100:3000 |
| Mosquitto MQTT | 192.168.1.100 | 1883 | mqtt://192.168.1.100:1883 |
| InfluxDB | 192.168.1.100 | 8086 | http://192.168.1.100:8086 |
| Node-RED | 192.168.1.100 | 1880 | http://192.168.1.100:1880 |
| Grafana | 192.168.1.100 | 3001 | http://192.168.1.100:3001 |
| Nodo ESP32 #1 | 192.168.1.51 | - | - |
| Nodo ESP32 #2 | 192.168.1.52 | - | - |
| Nodo ESP32 #3 | 192.168.1.53 | - | - |
| Robot ACEBOT | 192.168.4.1 | 80 | http://192.168.4.1 |

---

**\u00a1Listo!** Tu sistema IoT agr\u00edcola est\u00e1 completamente configurado y funcional.
