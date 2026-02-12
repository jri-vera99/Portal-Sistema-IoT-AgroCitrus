import paho.mqtt.client as mqtt
import json
import logging
from typing import Callable, Dict, Any
from config import MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD
from config import MQTT_TOPIC_SENSORS, MQTT_TOPIC_ROBOT_STATUS, MQTT_TOPIC_ROBOT_CONTROL

logger = logging.getLogger(__name__)

class MQTTManager:
    def __init__(self):
        self.client = mqtt.Client(client_id="fastapi_backend", protocol=mqtt.MQTTv311)
        self.broker = MQTT_BROKER
        self.port = MQTT_PORT
        self.connected = False
        self.callbacks: Dict[str, Callable] = {}
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Set credentials if provided
        if MQTT_USERNAME:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            logger.warning("MQTT running in simulation mode")
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker successfully")
            
            # Subscribe to topics
            self.client.subscribe(MQTT_TOPIC_SENSORS)
            self.client.subscribe(MQTT_TOPIC_ROBOT_STATUS)
            logger.info(f"Subscribed to topics: {MQTT_TOPIC_SENSORS}, {MQTT_TOPIC_ROBOT_STATUS}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker. Return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode('utf-8'))
            logger.debug(f"Received message on topic {topic}: {payload}")
            
            # Call registered callbacks
            for pattern, callback in self.callbacks.items():
                if self._topic_matches(pattern, topic):
                    callback(topic, payload)
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _topic_matches(self, pattern: str, topic: str) -> bool:
        """Check if topic matches pattern (supports # wildcard)"""
        pattern_parts = pattern.split('/')
        topic_parts = topic.split('/')
        
        for i, part in enumerate(pattern_parts):
            if part == '#':
                return True
            if i >= len(topic_parts):
                return False
            if part != '+' and part != topic_parts[i]:
                return False
        
        return len(pattern_parts) == len(topic_parts)
    
    def register_callback(self, topic_pattern: str, callback: Callable):
        """Register callback for topic pattern"""
        self.callbacks[topic_pattern] = callback
        logger.info(f"Registered callback for topic pattern: {topic_pattern}")
    
    def publish(self, topic: str, payload: Dict[Any, Any]):
        """Publish message to MQTT topic"""
        try:
            if self.connected:
                message = json.dumps(payload)
                result = self.client.publish(topic, message, qos=1)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.info(f"Published to {topic}: {payload}")
                else:
                    logger.error(f"Failed to publish to {topic}")
            else:
                logger.warning(f"Not connected to MQTT broker. Simulated publish to {topic}: {payload}")
        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}")
    
    def send_robot_command(self, command_type: str, parameters: Dict[Any, Any] = None):
        """Send command to robot"""
        payload = {
            "command": command_type,
            "parameters": parameters or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.publish(MQTT_TOPIC_ROBOT_CONTROL, payload)

from datetime import datetime, timezone

mqtt_manager = MQTTManager()