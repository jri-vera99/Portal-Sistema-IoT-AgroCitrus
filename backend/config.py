import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Database
MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']
SQLITE_DB = ROOT_DIR / 'iot_agriculture.db'

# JWT
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# MQTT
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', '1883'))
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', '')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')

# MQTT Topics
MQTT_TOPIC_SENSORS = 'citrus/sensors/#'
MQTT_TOPIC_ROBOT_STATUS = 'citrus/robot/status'
MQTT_TOPIC_ROBOT_CONTROL = 'citrus/robot/control'
MQTT_TOPIC_ALERTS = 'citrus/alerts'

# InfluxDB
INFLUXDB_URL = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN', '')
INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG', 'citrus_org')
INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET', 'citrus_sensors')

# OpenAI (Emergent LLM Key)
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# CORS
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

# Grafana
GRAFANA_URL = os.environ.get('GRAFANA_URL', 'http://localhost:3001')