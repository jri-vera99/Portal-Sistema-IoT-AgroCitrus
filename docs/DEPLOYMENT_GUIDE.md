# Guía de Despliegue en Raspberry Pi

## 🎯 Objetivo

Desplegar completamente el Sistema IoT Agrícola en Raspberry Pi 4/5 para uso en producción.

## 📦 Requisitos

### Hardware
- **Raspberry Pi 4 o 5** (4GB RAM mínimo, 8GB recomendado)
- **MicroSD 32GB+** (Clase 10, A2)
- **Fuente 5V 3A** (USB-C para Pi 4/5)
- **Red WiFi o Ethernet**
- **Opcional**: Ventilador o disipador

### Software
- **Raspberry Pi OS** (64-bit, Lite o Desktop)
- **Python 3.11+**
- **Node.js 18+**
- **Docker** (opcional, para servicios)

## 🛠️ Preparación del Sistema

### 1. Instalar Raspberry Pi OS

```bash
# Usar Raspberry Pi Imager
# https://www.raspberrypi.com/software/

# Configurar:
# - Hostname: citrus-iot-pi
# - Enable SSH
# - Set username/password
# - Configure WiFi
```

### 2. Actualización Inicial

```bash
# Conectar vía SSH
ssh pi@citrus-iot-pi.local

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar herramientas básicas
sudo apt install -y git curl wget vim htop net-tools

# Configurar zona horaria
sudo timedatectl set-timezone America/Lima

# Reiniciar
sudo reboot
```

### 3. Instalar Docker (Recomendado)

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install -y docker-compose

# Verificar
docker --version
docker-compose --version
```

## 📥 Instalación de Servicios

### Método 1: Usando Docker Compose (Recomendado)

#### Crear docker-compose.yml

```yaml
version: '3.8'

services:
  # MongoDB
  mongodb:
    image: mongo:7
    container_name: citrus-mongodb
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: citrus_iot

  # InfluxDB
  influxdb:
    image: influxdb:2.7
    container_name: citrus-influxdb
    restart: always
    ports:
      - "8086:8086"
    volumes:
      - influxdb_data:/var/lib/influxdb2
      - influxdb_config:/etc/influxdb2
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: citrus2025
      DOCKER_INFLUXDB_INIT_ORG: citrus_org
      DOCKER_INFLUXDB_INIT_BUCKET: citrus_sensors
      DOCKER_INFLUXDB_INIT_RETENTION: 1y
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: citrus-token-2025-secure

  # Mosquitto MQTT
  mosquitto:
    image: eclipse-mosquitto:2
    container_name: citrus-mosquitto
    restart: always
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/data:/mosquitto/data
      - ./mosquitto/log:/mosquitto/log

  # Grafana
  grafana:
    image: grafana/grafana-oss:latest
    container_name: citrus-grafana
    restart: always
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: citrus2025
      GF_SERVER_ROOT_URL: http://localhost:3001
    depends_on:
      - influxdb

  # Node-RED
  nodered:
    image: nodered/node-red:latest
    container_name: citrus-nodered
    restart: always
    ports:
      - "1880:1880"
    volumes:
      - nodered_data:/data
    environment:
      TZ: America/Lima
    depends_on:
      - mosquitto
      - influxdb

volumes:
  mongodb_data:
  influxdb_data:
  influxdb_config:
  grafana_data:
  nodered_data:
```

#### Configurar Mosquitto

```bash
# Crear directorio de configuración
mkdir -p mosquitto/config mosquitto/data mosquitto/log

# Crear archivo de configuración
cat > mosquitto/config/mosquitto.conf << EOF
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
EOF

# Permisos
sudo chown -R 1883:1883 mosquitto/
```

#### Iniciar Servicios

```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### Método 2: Instalación Nativa

#### MongoDB

```bash
# Importar clave pública
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Agregar repositorio
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/debian bullseye/mongodb-org/7.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Instalar
sudo apt update
sudo apt install -y mongodb-org

# Habilitar y iniciar
sudo systemctl enable mongod
sudo systemctl start mongod
```

#### InfluxDB

```bash
# Instalar
wget https://dl.influxdata.com/influxdb/releases/influxdb2-2.7.5-arm64.deb
sudo dpkg -i influxdb2-2.7.5-arm64.deb

# Iniciar
sudo systemctl enable influxdb
sudo systemctl start influxdb

# Configurar
influx setup \
  --username admin \
  --password citrus2025 \
  --org citrus_org \
  --bucket citrus_sensors \
  --retention 8760h \
  --force
```

#### Mosquitto

```bash
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

#### Grafana

```bash
# Ver guía GRAFANA_GUIDE.md
```

#### Node-RED

```bash
# Ver guía NODE_RED_GUIDE.md
```

## 💻 Despliegue de la Aplicación

### 1. Clonar Repositorio

```bash
cd /opt
sudo git clone <tu-repositorio> citrus-iot
sudo chown -R $USER:$USER citrus-iot
cd citrus-iot
```

### 2. Backend (FastAPI)

```bash
cd /opt/citrus-iot/backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
vim .env  # Editar configuración

# Probar
uvicorn server:app --host 0.0.0.0 --port 8001
```

#### Crear Servicio Systemd

```bash
sudo nano /etc/systemd/system/citrus-backend.service
```

```ini
[Unit]
Description=Citrus IoT Backend API
After=network.target mongodb.service influxdb.service

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/citrus-iot/backend
Environment="PATH=/opt/citrus-iot/backend/venv/bin"
ExecStart=/opt/citrus-iot/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable citrus-backend
sudo systemctl start citrus-backend
sudo systemctl status citrus-backend
```

### 3. Frontend (React)

```bash
cd /opt/citrus-iot/frontend

# Instalar dependencias
npm install

# Build de producción
npm run build

# Servir con nginx
sudo apt install -y nginx

sudo nano /etc/nginx/sites-available/citrus-iot
```

```nginx
server {
    listen 80;
    server_name citrus-iot-pi.local;

    root /opt/citrus-iot/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8001/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/citrus-iot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Configurar Firewall

```bash
sudo apt install -y ufw

sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 1880/tcp  # Node-RED
sudo ufw allow 3001/tcp  # Grafana
sudo ufw allow 1883/tcp  # MQTT

sudo ufw enable
sudo ufw status
```

## 🔐 Seguridad

### 1. SSL/TLS con Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx -d citrus-iot.tudominio.com

# Auto-renovación
sudo systemctl enable certbot.timer
```

### 2. Autenticación MQTT

```bash
# Crear usuario
sudo mosquitto_passwd -c /etc/mosquitto/passwd citrus_user

# Actualizar configuración
sudo nano /etc/mosquitto/mosquitto.conf
```

```
allow_anonymous false
password_file /etc/mosquitto/passwd
```

### 3. Firewall para Servicios Internos

```bash
# Solo permitir MongoDB desde localhost
sudo ufw deny 27017

# Solo permitir InfluxDB desde localhost
sudo ufw deny 8086
```

## 📊 Monitoreo

### Ver Logs

```bash
# Backend
sudo journalctl -u citrus-backend -f

# Nginx
sudo tail -f /var/log/nginx/access.log

# Docker services
docker-compose logs -f
```

### Monitoreo de Recursos

```bash
# CPU/RAM en tiempo real
htop

# Uso de disco
df -h

# Temperatura de la Pi
vcgencmd measure_temp
```

## 🔄 Backup

### Script de Backup

```bash
sudo nano /opt/citrus-iot/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/citrus-iot/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup SQLite
cp /opt/citrus-iot/backend/iot_agriculture.db $BACKUP_DIR/db_$DATE.db

# Backup InfluxDB
docker exec citrus-influxdb influx backup /tmp/backup_$DATE
docker cp citrus-influxdb:/tmp/backup_$DATE $BACKUP_DIR/influx_$DATE

# Limpiar backups antiguos (>30 días)
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completado: $DATE"
```

```bash
chmod +x /opt/citrus-iot/backup.sh

# Cron para backup diario
crontab -e
# Agregar: 0 2 * * * /opt/citrus-iot/backup.sh
```

## 🚀 Acceso Remoto

### Configurar DDNS (No-IP / DuckDNS)

```bash
# Ejemplo con DuckDNS
echo url="https://www.duckdns.org/update?domains=citrus-iot&token=tu-token&ip=" | curl -k -o ~/duckdns/duck.log -K -

# Cron cada 5 minutos
crontab -e
# */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

### Port Forwarding en Router

- Puerto 80 → Raspberry Pi:80 (HTTP)
- Puerto 443 → Raspberry Pi:443 (HTTPS)
- Puerto 1883 → Raspberry Pi:1883 (MQTT)

## ✅ Verificación Final

```bash
# Verificar servicios
sudo systemctl status citrus-backend
sudo systemctl status nginx
sudo systemctl status mosquitto
sudo systemctl status influxdb

# Test API
curl http://localhost:8001/api/

# Test MQTT
mosquitto_pub -h localhost -t "citrus/test" -m "hello"
mosquitto_sub -h localhost -t "citrus/test"

# Test InfluxDB
influx ping
```

## 📚 Recursos

- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [Docker on Raspberry Pi](https://docs.docker.com/engine/install/debian/)
- [Systemd Services](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**¡Sistema listo para producción!** Accede desde: http://citrus-iot-pi.local