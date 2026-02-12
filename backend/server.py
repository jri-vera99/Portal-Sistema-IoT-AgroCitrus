from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import logging
from typing import List, Optional, Dict

# Import configurations and modules
from config import CORS_ORIGINS, SQLITE_DB, GRAFANA_URL
from database import Database
from models import (
    UserCreate, UserLogin, Token, User, Alert, AlertAcknowledge,
    RobotStatus, RobotCommand, RobotCommandHistory, SensorReading,
    SensorHistoryQuery, AnalysisRequest, AnalysisResponse
)
from auth import verify_password, get_password_hash, create_access_token, get_current_user, get_current_admin_user
from influx_client import influx_manager
from mqtt_client import mqtt_manager
from ai_analysis import ai_analyzer
from user_routes import user_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
robot_status_cache = {
    "status": "idle",
    "battery_level": 85.0,
    "position": {"lat": -12.0464, "lon": -77.0428},
    "speed": 0.0,
    "heading": 0.0,
    "last_update": datetime.now(timezone.utc),
    "is_moving": False,
    "current_task": None
}

latest_sensor_readings = []

# Database instance
db = Database(SQLITE_DB)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting IoT Agriculture Platform...")
    
    # Initialize database
    await db.init_db()
    logger.info("Database initialized")
    
    # Create default admin user if not exists
    admin_user = await db.get_user_by_username("admin")
    if not admin_user:
        hashed_password = get_password_hash("admin123")
        await db.create_user("admin", "admin@citrus.iot", hashed_password, "Administrador", "admin")
        logger.info("Default admin user created: admin/admin123")
    
    # Connect to InfluxDB
    influx_manager.connect()
    
    # Connect to MQTT
    mqtt_manager.connect()
    
    # Register MQTT callbacks
    def on_sensor_data(topic: str, payload: dict):
        logger.info(f"Received sensor data: {topic} -> {payload}")
        # Store in InfluxDB
        if "node_id" in payload and "sensor_type" in payload and "value" in payload:
            influx_manager.write_sensor_data(
                payload["node_id"],
                payload["sensor_type"],
                payload["value"],
                payload.get("location")
            )
    
    def on_robot_status(topic: str, payload: dict):
        logger.info(f"Received robot status: {payload}")
        robot_status_cache.update({
            "status": payload.get("status", "idle"),
            "battery_level": payload.get("battery_level", 0),
            "position": payload.get("position", {"lat": 0, "lon": 0}),
            "speed": payload.get("speed", 0),
            "heading": payload.get("heading", 0),
            "last_update": datetime.now(timezone.utc),
            "is_moving": payload.get("is_moving", False),
            "current_task": payload.get("current_task")
        })
    
    mqtt_manager.register_callback("citrus/sensors/#", on_sensor_data)
    mqtt_manager.register_callback("citrus/robot/status", on_robot_status)
    
    logger.info("IoT Agriculture Platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down IoT Agriculture Platform...")
    influx_manager.close()
    mqtt_manager.disconnect()

# Create FastAPI app
app = FastAPI(
    title="Sistema IoT Agrícola - Cultivo de Mandarina",
    description="Plataforma de monitoreo microclimático con análisis predictivo",
    version="1.0.0",
    lifespan=lifespan
)

# Create API router
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== AUTHENTICATION ROUTES ====================

@api_router.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user exists
    existing_user = await db.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = await db.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user_id = await db.create_user(
        user_data.username,
        user_data.email,
        hashed_password,
        user_data.full_name,
        user_data.role
    )
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Return created user
    created_user = await db.get_user_by_username(user_data.username)
    return User(**created_user)

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user and return JWT token"""
    user = await db.get_user_by_username(credentials.username)
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "username": user["username"],
            "role": user["role"]
        }
    )
    
    return Token(access_token=access_token)

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    user = await db.get_user_by_username(current_user.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return User(**user)

# ==================== SENSOR ROUTES ====================

@api_router.get("/sensors/latest", response_model=List[SensorReading])
async def get_latest_sensor_readings(
    sensor_type: Optional[str] = None,
    node_id: Optional[str] = None,
    limit: int = 20,
    current_user = Depends(get_current_user)
):
    """Get latest sensor readings"""
    # Check user's simulation mode
    import json
    from pathlib import Path
    
    simulation_mode = False
    config_file = Path(__file__).parent / "config_admin.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            # Check if this specific user has simulation mode
            user_sims = config.get('user_simulations', {})
            simulation_mode = user_sims.get(str(current_user.id), False)
    
    readings = influx_manager.query_latest_readings(sensor_type, node_id, limit, simulation_mode)
    
    return [
        SensorReading(
            sensor_id=r["node_id"],
            sensor_type=r["sensor_type"],
            value=r["value"],
            unit=_get_unit(r["sensor_type"]),
            timestamp=datetime.fromisoformat(r["timestamp"].replace('Z', '+00:00'))
        )
        for r in readings
    ]

@api_router.post("/sensors/history")
async def get_sensor_history(
    query: SensorHistoryQuery,
    current_user = Depends(get_current_user)
):
    """Get historical sensor data"""
    # Check user's simulation mode
    import json
    from pathlib import Path
    
    simulation_mode = False
    config_file = Path(__file__).parent / "config_admin.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            user_sims = config.get('user_simulations', {})
            simulation_mode = user_sims.get(str(current_user.id), False)
    
    end_time = query.end_time or datetime.now(timezone.utc)
    start_time = query.start_time or (end_time - timedelta(hours=24))
    
    data = influx_manager.query_historical_data(
        query.sensor_type,
        start_time,
        end_time,
        query.node_id,
        query.aggregation,
        query.interval,
        simulation_mode
    )
    
    return {
        "sensor_type": query.sensor_type,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "data_points": len(data),
        "data": data
    }

# ==================== ALERT ROUTES ====================

@api_router.get("/alerts", response_model=List[Alert])
async def get_alerts(
    limit: int = 50,
    acknowledged: Optional[bool] = None,
    current_user = Depends(get_current_user)
):
    """Get alerts"""
    alerts = await db.get_alerts(limit, acknowledged)
    return [Alert(**alert) for alert in alerts]

@api_router.post("/alerts/acknowledge")
async def acknowledge_alert(
    data: AlertAcknowledge,
    current_user = Depends(get_current_user)
):
    """Acknowledge an alert"""
    await db.acknowledge_alert(data.alert_id, current_user.id)
    return {"status": "success", "message": "Alert acknowledged"}

# ==================== ROBOT ROUTES ====================

@api_router.get("/robot/status", response_model=RobotStatus)
async def get_robot_status(current_user = Depends(get_current_user)):
    """Get current robot status"""
    return RobotStatus(**robot_status_cache)

@api_router.post("/robot/control")
async def control_robot(
    command: RobotCommand,
    current_user = Depends(get_current_user)
):
    """Send control command to robot"""
    # Log command to database
    import json
    await db.create_robot_command(
        current_user.id,
        command.command_type,
        json.dumps(command.parameters) if command.parameters else None
    )
    
    # Send command via MQTT
    mqtt_manager.send_robot_command(command.command_type, command.parameters)
    
    return {
        "status": "success",
        "message": f"Command '{command.command_type}' sent to robot"
    }

@api_router.get("/robot/commands", response_model=List[RobotCommandHistory])
async def get_robot_commands(
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    """Get robot command history"""
    commands = await db.get_robot_commands(limit)
    return [RobotCommandHistory(**cmd) for cmd in commands]

# ==================== AI ANALYSIS ROUTES ====================

@api_router.post("/analysis/predict")
async def predict_analysis(
    request: AnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Get AI-powered predictive analysis"""
    result = await ai_analyzer.analyze_sensor_data(
        request.analysis_type,
        request.time_range_hours,
        request.node_id
    )
    return result

# ==================== ADMIN ROUTES ====================

@api_router.get("/admin/config")
async def get_admin_config(current_user = Depends(get_current_admin_user)):
    """Get system configuration (admin only)"""
    import json
    import os
    
    config_file = Path(__file__).parent / "config_admin.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # Default configuration
    return {
        "mqtt": {
            "broker": "localhost",
            "port": "1883",
            "username": "",
            "password": "",
            "enabled": False
        },
        "influxdb": {
            "url": INFLUXDB_URL,
            "token": "",
            "org": INFLUXDB_ORG,
            "bucket": INFLUXDB_BUCKET,
            "enabled": False
        },
        "robot": {
            "wifi_ssid": "ACEBOT-QD001",
            "wifi_password": "",
            "control_url": "http://192.168.4.1",
            "enabled": False
        },
        "nodes": [],
        "simulation_mode": True
    }

@api_router.post("/admin/config")
async def save_admin_config(config: Dict[str, Any], current_user = Depends(get_current_admin_user)):
    """Save system configuration (admin only)"""
    import json
    
    config_file = Path(__file__).parent / "config_admin.json"
    
    # Load existing config
    existing_config = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            existing_config = json.load(f)
    
    # Update with new config
    existing_config.update(config)
    
    # Save
    with open(config_file, 'w') as f:
        json.dump(existing_config, f, indent=2)
    
    # Apply configuration if needed
    if 'simulation_mode' in config:
        # Update simulation mode flag
        pass
    
    return {"status": "success", "message": "Configuración guardada"}

@api_router.post("/admin/test-connection")
async def test_connection(data: Dict[str, Any], current_user = Depends(get_current_admin_user)):
    """Test connection to external services (admin only)"""
    conn_type = data.get("type")
    config = data.get("config")
    
    if conn_type == "mqtt":
        try:
            import paho.mqtt.client as mqtt_test
            client = mqtt_test.Client("test_client")
            if config.get("username"):
                client.username_pw_set(config["username"], config.get("password", ""))
            client.connect(config["broker"], int(config["port"]), 5)
            client.disconnect()
            return {"status": "success", "message": "Conexión MQTT exitosa"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error MQTT: {str(e)}")
    
    elif conn_type == "influxdb":
        try:
            from influxdb_client import InfluxDBClient
            client = InfluxDBClient(url=config["url"], token=config["token"], org=config["org"])
            health = client.health()
            client.close()
            if health.status == "pass":
                return {"status": "success", "message": "Conexión InfluxDB exitosa"}
            else:
                raise HTTPException(status_code=400, detail="InfluxDB no está saludable")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error InfluxDB: {str(e)}")
    
    return {"status": "error", "message": "Tipo de conexión no válido"}

# ==================== SYSTEM ROUTES ====================

@api_router.get("/system/info")
async def get_system_info(current_user = Depends(get_current_user)):
    """Get system information"""
    return {
        "system_name": "Sistema IoT Agrícola - Cultivo de Mandarina",
        "version": "1.0.0",
        "mqtt_connected": mqtt_manager.connected,
        "influxdb_connected": influx_manager.client is not None,
        "grafana_url": GRAFANA_URL,
        "ai_enabled": bool(ai_analyzer.api_key)
    }

@api_router.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Sistema IoT Agrícola - API",
        "version": "1.0.0",
        "status": "running"
    }

# Helper function
def _get_unit(sensor_type: str) -> str:
    """Get unit for sensor type"""
    units = {
        "temperature": "°C",
        "air_humidity": "%",
        "soil_moisture": "%",
        "luminosity": "lux"
    }
    return units.get(sensor_type, "")

# Include router
app.include_router(api_router)
app.include_router(user_router)