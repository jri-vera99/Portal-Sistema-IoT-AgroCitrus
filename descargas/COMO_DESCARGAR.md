# 📥 Cómo Descargar el Proyecto

## Archivos Disponibles

He generado dos versiones del proyecto para que elijas la que prefieras:

### 1. **sistema-iot-agricola.zip** (323 KB) - Recomendado para Windows
- Formato ZIP universal
- Compatible con todos los sistemas operativos
- Se extrae con doble clic en Windows

### 2. **sistema-iot-agricola-completo.tar.gz** (285 KB) - Recomendado para macOS/Linux
- Formato comprimido TAR.GZ
- Mejor para sistemas Unix/Linux
- Mantiene permisos de archivos

## 📂 Contenido del Paquete

```
sistema-iot-agricola/
├── 📖 INSTALACION_LOCAL.md    ← ¡EMPIEZA AQUÍ! Guía paso a paso
├── 📖 README.md                ← Documentación completa del proyecto
│
├── 🔧 backend/                 ← Servidor FastAPI (Python)
│   ├── server.py
│   ├── config.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   ├── influx_client.py
│   ├── mqtt_client.py
│   ├── ai_analysis.py
│   ├── requirements.txt
│   └── .env
│
├── 🎨 frontend/                ← Aplicación React
│   ├── src/
│   │   ├── App.js
│   │   ├── api/api.js
│   │   ├── context/
│   │   ├── pages/
│   │   └── components/
│   ├── package.json
│   └── .env
│
└── 📚 docs/                    ← Documentación adicional
    ├── NODE_RED_GUIDE.md
    ├── GRAFANA_GUIDE.md
    ├── DEPLOYMENT_GUIDE.md
    └── ESP32_FIRMWARE_GUIDE.md
```

## 🚀 Pasos para Empezar

### Opción A: Usar el entorno actual (Emergent)

Si estás trabajando en la plataforma Emergent actual, el código ya está funcionando. Puedes:

1. Explorar los archivos en `/app/`
2. Modificar el código directamente
3. Los cambios se reflejan automáticamente

### Opción B: Descargar y trabajar localmente

Para trabajar en tu computadora local:

1. **Descargar los archivos desde el entorno Emergent**

   Puedes usar uno de estos métodos:

   **Método 1: Desde la terminal de Emergent**
   ```bash
   # Los archivos están en:
   /tmp/sistema-iot-agricola.zip         (para Windows)
   /tmp/sistema-iot-agricola-completo.tar.gz  (para macOS/Linux)
   ```

   **Método 2: Clonar el repositorio (si tienes GitHub conectado)**
   ```bash
   # Si has conectado tu repositorio GitHub a Emergent
   git clone [tu-repositorio]
   ```

2. **Extraer el archivo en tu computadora**

   **Windows:**
   - Doble clic en `sistema-iot-agricola.zip`
   - Clic derecho → Extraer todo
   - Elige una carpeta (ej: `C:\Users\TuUsuario\Proyectos\`)

   **macOS:**
   ```bash
   tar -xzf sistema-iot-agricola-completo.tar.gz
   cd sistema-iot-agricola
   ```

   **Linux:**
   ```bash
   tar -xzf sistema-iot-agricola-completo.tar.gz
   cd sistema-iot-agricola
   ```

3. **Abrir en Visual Studio Code**

   ```bash
   code .
   ```

   O desde VS Code: File → Open Folder → Selecciona la carpeta del proyecto

4. **Seguir la guía de instalación**

   Abre el archivo `INSTALACION_LOCAL.md` que está incluido en el paquete y sigue las instrucciones paso a paso.

## 📋 Requisitos Mínimos

- **Sistema Operativo:** Windows 10/11, macOS 10.15+, o Linux
- **RAM:** 4 GB mínimo (8 GB recomendado)
- **Disco:** 2 GB de espacio libre
- **Internet:** Para descargar dependencias

## ✅ Verificación Rápida

Después de extraer, verifica que tienes estos archivos clave:

```bash
# Backend
backend/server.py          ✓
backend/requirements.txt   ✓
backend/.env               ✓

# Frontend
frontend/package.json      ✓
frontend/src/App.js        ✓
frontend/.env              ✓

# Documentación
INSTALACION_LOCAL.md       ✓
README.md                  ✓
```

## 🔐 Credenciales por Defecto

Una vez que tengas el proyecto corriendo:

- **Usuario:** `admin`
- **Contraseña:** `admin123`

## 📞 Próximos Pasos

1. ✅ Extraer el archivo descargado
2. ✅ Abrir `INSTALACION_LOCAL.md`
3. ✅ Instalar Python 3.11+ y Node.js 18+
4. ✅ Seguir la guía paso a paso
5. ✅ ¡Empezar a desarrollar!

## 💡 Consejos

- **Primera vez con Python/Node.js?** No te preocupes, la guía `INSTALACION_LOCAL.md` explica todo desde cero
- **Problemas?** Consulta la sección "Solución de Problemas" en `INSTALACION_LOCAL.md`
- **¿Quieres deploy?** Lee `DEPLOYMENT_GUIDE.md` para desplegar en Raspberry Pi

## 🎓 Para tu Proyecto Universitario

El paquete incluye:
- ✅ Código fuente completo y comentado
- ✅ Documentación técnica profesional
- ✅ Guías de instalación y despliegue
- ✅ Arquitectura lista para presentar
- ✅ Diagramas y especificaciones

**¡Perfecto para tu presentación y defensa del proyecto!**

---

**¿Listo para empezar?** Extrae el archivo y abre `INSTALACION_LOCAL.md` 🚀
