from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    AGRICULTOR = "agricultor"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    HIGH_TEMPERATURE = "high_temperature"
    LOW_TEMPERATURE = "low_temperature"
    LOW_SOIL_MOISTURE = "low_soil_moisture"
    HIGH_SOIL_MOISTURE = "high_soil_moisture"
    LOW_AIR_HUMIDITY = "low_air_humidity"
    HIGH_LUMINOSITY = "high_luminosity"
    LOW_LUMINOSITY = "low_luminosity"
    ROBOT_OUT_OF_ZONE = "robot_out_of_zone"
    WATER_STRESS = "water_stress"
    SENSOR_ERROR = "sensor_error"

class RobotCommandType(str, Enum):
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    STOP = "stop"
    GO_TO_POSITION = "go_to_position"
    START_PATROL = "start_patrol"
    STOP_PATROL = "stop_patrol"
    RETURN_HOME = "return_home"

# Auth Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.AGRICULTOR

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: str
    is_active: int

class UserInToken(BaseModel):
    id: int
    username: str
    role: str

# Sensor Models
class SensorReading(BaseModel):
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    location: Optional[Dict[str, float]] = None

class SensorData(BaseModel):
    node_id: str
    timestamp: datetime
    temperature: Optional[float] = None
    air_humidity: Optional[float] = None
    soil_moisture: Optional[float] = None
    luminosity: Optional[float] = None
    location: Optional[Dict[str, float]] = None

class SensorHistoryQuery(BaseModel):
    sensor_type: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    node_id: Optional[str] = None
    aggregation: Optional[str] = "mean"
    interval: Optional[str] = "5m"

# Alert Models
class Alert(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    sensor_id: Optional[str]
    value: Optional[float]
    threshold: Optional[float]
    timestamp: str
    acknowledged: int
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[str]

class AlertAcknowledge(BaseModel):
    alert_id: int

# Robot Models
class RobotStatus(BaseModel):
    status: str
    battery_level: float
    position: Dict[str, float]
    speed: float
    heading: float
    last_update: datetime
    is_moving: bool
    current_task: Optional[str]

class RobotCommand(BaseModel):
    command_type: RobotCommandType
    parameters: Optional[Dict[str, Any]] = None

class RobotCommandHistory(BaseModel):
    id: int
    user_id: int
    command_type: str
    command_data: Optional[str]
    status: str
    timestamp: str

# AI Analysis Models
class AnalysisRequest(BaseModel):
    analysis_type: str = "general"
    time_range_hours: int = 24
    node_id: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis_type: str
    summary: str
    predictions: List[Dict[str, Any]]
    recommendations: List[str]
    risk_level: str
    timestamp: datetime