# 📦 Sistema IoT Agrícola - Paquete de Descarga

## 🎉 ¡Tu proyecto está listo para descargar!

He preparado todo el código fuente del **Sistema IoT para Monitoreo de Condiciones Microclimáticas en el Cultivo de Mandarina** para que lo ejecutes localmente en tu computadora.

---

## 📥 Archivos Disponibles

Los archivos están ubicados en: `/app/descargas/`

### 🗂️ Opción 1: ZIP (Recomendado para Windows)
```
📦 sistema-iot-agricola.zip (323 KB)
```
- Formato universal
- Compatible con Windows, macOS y Linux
- Se extrae con doble clic

### 🗂️ Opción 2: TAR.GZ (Recomendado para macOS/Linux)
```
📦 sistema-iot-agricola-completo.tar.gz (285 KB)
```
- Formato comprimido optimizado
- Mantiene permisos de archivos
- Ideal para sistemas Unix/Linux

---

## 📖 Documentación Incluida

### 1. **INSTALACION_LOCAL.md** ⭐ ¡EMPIEZA AQUÍ!
Guía completa paso a paso para:
- ✅ Instalar Python y Node.js
- ✅ Configurar el entorno de desarrollo
- ✅ Ejecutar backend y frontend
- ✅ Probar la aplicación
- ✅ Solucionar problemas comunes

### 2. **COMO_DESCARGAR.md**
Instrucciones para obtener y extraer los archivos

### 3. **README.md**
Documentación completa del proyecto con:
- Arquitectura del sistema
- Endpoints de la API
- Estructura del proyecto
- Guía de uso

### 4. **docs/** (Carpeta con guías adicionales)
- `NODE_RED_GUIDE.md` - Integración con Node-RED
- `GRAFANA_GUIDE.md` - Dashboards en Grafana
- `DEPLOYMENT_GUIDE.md` - Despliegue en Raspberry Pi
- `ESP32_FIRMWARE_GUIDE.md` - Código para dispositivos ESP32

---

## 🚀 Inicio Rápido

### Para Windows:

1. **Descargar** `sistema-iot-agricola.zip` desde `/app/descargas/`
2. **Extraer** el archivo (clic derecho → Extraer todo)
3. **Abrir** la carpeta en Visual Studio Code
4. **Leer** `INSTALACION_LOCAL.md` y seguir los pasos

### Para macOS/Linux:

```bash
# Navegar al directorio de descargas
cd /app/descargas/

# Extraer el archivo
tar -xzf sistema-iot-agricola-completo.tar.gz

# Entrar al proyecto
cd sistema-iot-agricola

# Abrir en VS Code
code .

# Leer la guía de instalación
cat INSTALACION_LOCAL.md
```

---

## 💻 Lo que incluye el paquete

### Backend (Python + FastAPI)
- ✅ API REST completa
- ✅ Autenticación JWT
- ✅ Base de datos SQLite
- ✅ Integración con InfluxDB y MQTT
- ✅ Análisis con IA (OpenAI GPT-4o-mini)
- ✅ Sistema de alertas

### Frontend (React)
- ✅ Dashboard moderno e intuitivo
- ✅ Visualización en tiempo real
- ✅ Gráficos con Recharts
- ✅ Control del robot móvil
- ✅ Panel de alertas
- ✅ Análisis predictivo con IA

### Documentación
- ✅ Guías de instalación
- ✅ Documentación técnica
- ✅ Código comentado
- ✅ Arquitectura del sistema
- ✅ Guías de deployment

---

## 🔧 Requisitos del Sistema

Para ejecutar el proyecto necesitas:

### Software:
- **Python 3.11+** → [Descargar](https://www.python.org/downloads/)
- **Node.js 18+** → [Descargar](https://nodejs.org/)
- **Visual Studio Code** → [Descargar](https://code.visualstudio.com/)

### Hardware Mínimo:
- **RAM:** 4 GB (8 GB recomendado)
- **Disco:** 2 GB de espacio libre
- **Sistema Operativo:** Windows 10/11, macOS 10.15+, o Linux

---

## 🎯 Credenciales por Defecto

Una vez que ejecutes la aplicación:

```
Usuario: admin
Contraseña: admin123
```

Accede a: `http://localhost:3000`

---

## 📊 Características Principales

### Dashboard Principal
- 📈 Visualización de temperatura, humedad y luminosidad
- 📊 Gráficos históricos de 24 horas
- 🔔 Sistema de alertas en tiempo real
- 🤖 Estado del robot y batería

### Control del Robot
- ⬆️ Controles manuales (adelante, atrás, izquierda, derecha)
- 🏠 Comandos automatizados (volver a base, patrullar)
- 📍 Seguimiento GPS
- 🔋 Monitoreo de batería

### Análisis con IA
- 🧠 Análisis predictivo de cultivo
- 📉 Detección de tendencias
- 💡 Recomendaciones agronómicas
- ⚠️ Evaluación de riesgo

---

## 📁 Estructura del Proyecto

```
sistema-iot-agricola/
│
├── 📖 INSTALACION_LOCAL.md    ← Lee esto primero
├── 📖 README.md
├── 📖 COMO_DESCARGAR.md
│
├── backend/                   ← API FastAPI
│   ├── server.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   ├── ai_analysis.py
│   └── requirements.txt
│
├── frontend/                  ← Aplicación React
│   ├── src/
│   ├── public/
│   └── package.json
│
└── docs/                      ← Documentación adicional
    ├── NODE_RED_GUIDE.md
    ├── GRAFANA_GUIDE.md
    ├── DEPLOYMENT_GUIDE.md
    └── ESP32_FIRMWARE_GUIDE.md
```

---

## ⚡ Comandos Rápidos

Una vez que hayas extraído el proyecto:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --host 127.0.0.1 --port 8001

# Frontend (en otra terminal)
cd frontend
npm install
npm start
```

---

## 🎓 Perfecto para Proyecto Universitario

El paquete incluye todo lo necesario para:

- ✅ **Presentación**: Documentación profesional y clara
- ✅ **Defensa**: Arquitectura bien definida
- ✅ **Demostración**: Sistema funcionando end-to-end
- ✅ **Código**: Comentado y bien estructurado
- ✅ **Escalabilidad**: Base para mejoras futuras

---

## 🔍 Verificación de Descarga

Después de extraer, verifica que tienes:

```
✓ backend/server.py
✓ backend/requirements.txt
✓ frontend/package.json
✓ frontend/src/App.js
✓ INSTALACION_LOCAL.md
✓ README.md
✓ docs/ (carpeta con 4 archivos)
```

---

## 📞 Próximos Pasos

1. ✅ **Descargar** uno de los archivos desde `/app/descargas/`
2. ✅ **Extraer** en tu computadora
3. ✅ **Abrir** `INSTALACION_LOCAL.md`
4. ✅ **Instalar** Python y Node.js
5. ✅ **Ejecutar** backend y frontend
6. ✅ **Explorar** el dashboard en tu navegador

---

## 💡 Consejos Importantes

- 📖 **Lee `INSTALACION_LOCAL.md` primero** - Tiene todo explicado paso a paso
- 🔄 **Ambos servidores deben estar corriendo** - Backend (puerto 8001) y Frontend (puerto 3000)
- 🌐 **Accede desde tu navegador** - http://localhost:3000
- 🐛 **¿Problemas?** - Revisa la sección de troubleshooting en la guía

---

## 🎁 Bonus: Modo Simulación

El sistema funciona **sin necesidad de hardware físico**:

- ✅ Datos de sensores simulados automáticamente
- ✅ Robot virtual con GPS simulado
- ✅ Alertas y análisis completamente funcionales
- ✅ Perfecto para desarrollo y demostración

Cuando tengas los ESP32 reales, solo necesitas:
1. Flashear el firmware (guía incluida en `docs/ESP32_FIRMWARE_GUIDE.md`)
2. Instalar InfluxDB y Mosquitto MQTT
3. ¡Los datos reales reemplazarán los simulados!

---

## 🌟 ¡Listo para Empezar!

Tu sistema IoT agrícola completo está en:
```
📂 /app/descargas/
```

**¡Descarga, extrae y comienza a desarrollar!** 🚀

---

**Desarrollado con:** FastAPI • React • InfluxDB • MQTT • OpenAI • Tailwind CSS

**Proyecto Universitario 2025** - Sistema IoT para Cultivo de Mandarina
