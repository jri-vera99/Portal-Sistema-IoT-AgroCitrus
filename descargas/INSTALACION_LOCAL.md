# 🚀 Guía de Instalación Local - Sistema IoT Agrícola

## 📋 Requisitos Previos

### Software Necesario:
- **Python 3.11+** - [Descargar](https://www.python.org/downloads/)
- **Node.js 18+** - [Descargar](https://nodejs.org/)
- **Visual Studio Code** - [Descargar](https://code.visualstudio.com/)
- **Git** (opcional) - [Descargar](https://git-scm.com/)

### Extensiones Recomendadas para VS Code:
- Python (Microsoft)
- Pylance (Microsoft)
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- Thunder Client (para probar APIs)

---

## 📥 Paso 1: Descargar y Extraer el Proyecto

1. Descarga el archivo `sistema-iot-agricola.tar.gz`
2. Extrae el archivo en tu carpeta de proyectos

**Windows (usando 7-Zip o WinRAR):**
```
Clic derecho → Extraer aquí
```

**macOS/Linux:**
```bash
tar -xzf sistema-iot-agricola.tar.gz
cd sistema-iot-agricola
```

---

## 🔧 Paso 2: Configurar el Backend

### 2.1 Abrir en VS Code
```bash
cd sistema-iot-agricola
code .
```

### 2.2 Crear Entorno Virtual

**Windows (PowerShell):**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Instalar Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Configurar Variables de Entorno

Crea o edita el archivo `backend/.env`:

```env
# Base de datos
MONGO_URL="mongodb://localhost:27017"
DB_NAME="citrus_iot_local"

# JWT
SECRET_KEY="tu-clave-secreta-muy-segura-2025"

# MQTT (opcional - dejar vacío para modo simulación)
MQTT_BROKER="localhost"
MQTT_PORT="1883"
MQTT_USERNAME=""
MQTT_PASSWORD=""

# InfluxDB (opcional - dejar vacío para modo simulación)
INFLUXDB_URL="http://localhost:8086"
INFLUXDB_TOKEN=""
INFLUXDB_ORG="citrus_org"
INFLUXDB_BUCKET="citrus_sensors"

# Grafana
GRAFANA_URL="http://localhost:3001"

# IA - Clave Universal de Emergent (ya incluida)
EMERGENT_LLM_KEY=sk-emergent-c96Ff3e558c1d87F93

# CORS
CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
```

### 2.5 Iniciar el Backend

**Terminal 1 (en VS Code):**
```bash
cd backend
# Activar entorno virtual si no está activo
uvicorn server:app --reload --host 127.0.0.1 --port 8001
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
```

🔍 **Verificar:** Abre http://127.0.0.1:8001/api/ en tu navegador
Deberías ver: `{"message": "Sistema IoT Agrícola - API", "version": "1.0.0", "status": "running"}`

---

## 🎨 Paso 3: Configurar el Frontend

### 3.1 Abrir Nueva Terminal en VS Code
Presiona `Ctrl + Shift + ñ` (o desde el menú: Terminal → New Terminal)

### 3.2 Instalar Dependencias

**Terminal 2:**
```bash
cd frontend
npm install
# o si prefieres yarn:
# yarn install
```

### 3.3 Configurar Variables de Entorno

Crea o edita el archivo `frontend/.env`:

```env
REACT_APP_BACKEND_URL=http://127.0.0.1:8001
```

### 3.4 Iniciar el Frontend

**Terminal 2:**
```bash
npm start
# o
# yarn start
```

El navegador se abrirá automáticamente en http://localhost:3000

---

## 🎉 Paso 4: Probar la Aplicación

### 4.1 Login
- **Usuario:** `admin`
- **Contraseña:** `admin123`

### 4.2 Explorar las Funcionalidades

1. **Dashboard Principal**
   - Ver métricas de sensores en tiempo real
   - Gráficos históricos de 24 horas
   - Estado del sistema

2. **Tab Sensores**
   - Visualización detallada de todos los sensores
   - Tabla de lecturas recientes

3. **Tab Alertas**
   - Ver alertas del sistema
   - Reconocer alertas

4. **Tab Robot**
   - Control manual del robot
   - Comandos automatizados
   - Estado de batería y posición

5. **Tab Análisis IA**
   - Ejecutar análisis predictivo
   - Ver recomendaciones
   - Análisis de riesgo del cultivo

---

## 🧪 Paso 5: Probar la API (Opcional)

### Usando Thunder Client en VS Code:

1. Instala la extensión "Thunder Client"
2. Crea una nueva Request
3. **Login:**
   ```
   Method: POST
   URL: http://127.0.0.1:8001/api/auth/login
   Body (JSON):
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
4. Copia el `access_token` de la respuesta
5. **Obtener Sensores:**
   ```
   Method: GET
   URL: http://127.0.0.1:8001/api/sensors/latest
   Headers:
   Authorization: Bearer [tu-token-aquí]
   ```

### Usando cURL (Terminal):

```bash
# Login
curl -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Obtener sensores (reemplaza TOKEN con el token obtenido)
curl -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:8001/api/sensors/latest
```

---

## 📊 Paso 6: Servicios Opcionales (Avanzado)

### MongoDB (Opcional - pero recomendado)

**Windows (usando Chocolatey):**
```powershell
choco install mongodb
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

Luego actualiza `backend/.env`:
```env
MONGO_URL="mongodb://localhost:27017"
```

### InfluxDB 2.x (Opcional)

**Windows/macOS/Linux:**
Descargar desde: https://portal.influxdata.com/downloads/

Después de instalar:
```bash
influx setup --username admin --password citrus2025 --org citrus_org --bucket citrus_sensors
```

Copia el token generado y actualiza `backend/.env`:
```env
INFLUXDB_TOKEN="tu-token-aquí"
```

### Mosquitto MQTT (Opcional)

**Windows:**
Descargar desde: https://mosquitto.org/download/

**macOS:**
```bash
brew install mosquitto
brew services start mosquitto
```

**Linux:**
```bash
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl start mosquitto
```

---

## 🐛 Solución de Problemas Comunes

### Error: "Python no se reconoce como comando"
**Solución:** Asegúrate de que Python está en el PATH del sistema
- Windows: Reinstala Python y marca "Add Python to PATH"

### Error: "node no se reconoce como comando"
**Solución:** Reinstala Node.js y reinicia VS Code

### Error: "puerto 8001 ya está en uso"
**Solución:** 
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID [número] /F

# macOS/Linux
lsof -ti:8001 | xargs kill -9
```

### Error: "npm install falla"
**Solución:**
```bash
# Limpiar caché
npm cache clean --force
# Borrar node_modules
rm -rf node_modules package-lock.json
# Reinstalar
npm install
```

### Backend funciona pero Frontend no conecta
**Solución:** Verifica que `frontend/.env` tenga:
```env
REACT_APP_BACKEND_URL=http://127.0.0.1:8001
```

### Datos no aparecen en el Dashboard
**Solución:** El sistema está en modo simulación. Los datos se generan automáticamente. Si no aparecen:
1. Verifica que el backend esté corriendo
2. Revisa la consola del navegador (F12) para errores
3. Verifica que el token de autenticación sea válido

---

## 📁 Estructura del Proyecto

```
sistema-iot-agricola/
├── backend/
│   ├── server.py              # Servidor principal FastAPI
│   ├── config.py              # Configuración
│   ├── models.py              # Modelos Pydantic
│   ├── database.py            # SQLite
│   ├── auth.py                # Autenticación JWT
│   ├── influx_client.py       # Cliente InfluxDB
│   ├── mqtt_client.py         # Cliente MQTT
│   ├── ai_analysis.py         # Análisis con IA
│   ├── requirements.txt       # Dependencias Python
│   └── .env                   # Variables de entorno
│
├── frontend/
│   ├── src/
│   │   ├── App.js             # Componente principal
│   │   ├── index.js           # Entry point
│   │   ├── api/api.js         # Cliente API
│   │   ├── context/           # Contextos React
│   │   ├── pages/             # Páginas (Login, Dashboard)
│   │   └── components/        # Componentes reutilizables
│   ├── public/
│   ├── package.json           # Dependencias Node
│   └── .env                   # Variables de entorno
│
├── docs/
│   ├── NODE_RED_GUIDE.md      # Guía Node-RED
│   ├── GRAFANA_GUIDE.md       # Guía Grafana
│   ├── DEPLOYMENT_GUIDE.md    # Despliegue Raspberry Pi
│   └── ESP32_FIRMWARE_GUIDE.md # Firmware ESP32
│
└── README.md                  # Documentación principal
```

---

## 🔄 Comandos Útiles

### Backend
```bash
# Iniciar servidor
uvicorn server:app --reload --host 127.0.0.1 --port 8001

# Ver logs en tiempo real
# (Los logs aparecen en la terminal donde corre uvicorn)

# Instalar nueva dependencia
pip install <paquete>
pip freeze > requirements.txt
```

### Frontend
```bash
# Iniciar desarrollo
npm start

# Build para producción
npm run build

# Instalar nueva dependencia
npm install <paquete>
```

---

## 🎓 Recursos de Aprendizaje

- **FastAPI:** https://fastapi.tiangolo.com/
- **React:** https://react.dev/
- **Recharts:** https://recharts.org/
- **Tailwind CSS:** https://tailwindcss.com/
- **InfluxDB:** https://docs.influxdata.com/
- **MQTT:** https://mqtt.org/

---

## 💡 Consejos para Desarrollo

1. **Hot Reload:** Ambos servidores se recargan automáticamente al guardar cambios
2. **Depuración:** 
   - Backend: Usa `print()` o el debugger de VS Code
   - Frontend: Usa `console.log()` y React DevTools
3. **Git:** Inicializa un repositorio para control de versiones:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs de la terminal donde corre cada servicio
2. Verifica la consola del navegador (F12)
3. Consulta la documentación en `/docs`
4. Revisa el README.md principal

---

## ✅ Checklist de Verificación

- [ ] Python 3.11+ instalado
- [ ] Node.js 18+ instalado
- [ ] Backend corriendo en http://127.0.0.1:8001
- [ ] Frontend corriendo en http://localhost:3000
- [ ] Login exitoso con admin/admin123
- [ ] Dashboard mostrando datos de sensores
- [ ] API respondiendo correctamente

**¡Listo para desarrollar!** 🚀
