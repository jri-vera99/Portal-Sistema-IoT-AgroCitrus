from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging
from config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET

logger = logging.getLogger(__name__)

class InfluxDBManager:
    def __init__(self):
        self.url = INFLUXDB_URL
        self.token = INFLUXDB_TOKEN
        self.org = INFLUXDB_ORG
        self.bucket = INFLUXDB_BUCKET
        self.client = None
        self.write_api = None
        self.query_api = None
        
    def connect(self):
        """Connect to InfluxDB"""
        try:
            if self.token:
                self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                self.query_api = self.client.query_api()
                logger.info(f"Connected to InfluxDB at {self.url}")
            else:
                logger.warning("InfluxDB token not configured, running in simulation mode")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
    
    def close(self):
        """Close InfluxDB connection"""
        if self.client:
            self.client.close()
            logger.info("InfluxDB connection closed")
    
    def write_sensor_data(self, node_id: str, sensor_type: str, value: float, 
                         location: Optional[Dict[str, float]] = None):
        """Write sensor data to InfluxDB"""
        if not self.write_api:
            logger.warning("InfluxDB not connected, skipping write")
            return
        
        try:
            point = Point("sensor_reading") \
                .tag("node_id", node_id) \
                .tag("sensor_type", sensor_type) \
                .field("value", float(value))
            
            if location:
                point = point.tag("latitude", str(location.get("lat", 0))) \
                           .tag("longitude", str(location.get("lon", 0)))
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            logger.debug(f"Written to InfluxDB: {node_id}/{sensor_type}={value}")
        except Exception as e:
            logger.error(f"Failed to write to InfluxDB: {e}")
    
    def query_latest_readings(self, sensor_type: Optional[str] = None, 
                             node_id: Optional[str] = None, limit: int = 10, 
                             simulation_mode: bool = False) -> List[Dict]:
        """Query latest sensor readings"""
        # Check if we should use simulated data
        if simulation_mode or not self.query_api:
            logger.warning("Using simulated data (simulation_mode={}, query_api={})".format(
                simulation_mode, self.query_api is not None))
            return self._get_simulated_data(sensor_type, node_id, limit)
        
        try:
            filter_clause = f'r._measurement == "sensor_reading"'
            if sensor_type:
                filter_clause += f' and r.sensor_type == "{sensor_type}"'
            if node_id:
                filter_clause += f' and r.node_id == "{node_id}"'
            
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -1h)
                |> filter(fn: (r) => {filter_clause})
                |> last()
                |> limit(n: {limit})
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            readings = []
            for table in result:
                for record in table.records:
                    readings.append({
                        "node_id": record.values.get("node_id"),
                        "sensor_type": record.values.get("sensor_type"),
                        "value": record.values.get("_value"),
                        "timestamp": record.values.get("_time").isoformat()
                    })
            
            return readings
        except Exception as e:
            logger.error(f"Failed to query InfluxDB: {e}")
            return []
    
    def query_historical_data(self, sensor_type: str, start_time: datetime, 
                             end_time: datetime, node_id: Optional[str] = None,
                             aggregation: str = "mean", interval: str = "5m",
                             simulation_mode: bool = False) -> List[Dict]:
        """Query historical sensor data with aggregation"""
        # Check if we should use simulated data
        if simulation_mode or not self.query_api:
            logger.warning("Using simulated historical data")
            return self._get_simulated_historical_data(sensor_type, start_time, end_time)
        
        try:
            filter_clause = f'r._measurement == "sensor_reading" and r.sensor_type == "{sensor_type}"'
            if node_id:
                filter_clause += f' and r.node_id == "{node_id}"'
            
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
                |> filter(fn: (r) => {filter_clause})
                |> aggregateWindow(every: {interval}, fn: {aggregation}, createEmpty: false)
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            data_points = []
            for table in result:
                for record in table.records:
                    data_points.append({
                        "timestamp": record.values.get("_time").isoformat(),
                        "value": record.values.get("_value"),
                        "node_id": record.values.get("node_id")
                    })
            
            return data_points
        except Exception as e:
            logger.error(f"Failed to query historical data: {e}")
            return []
    
    def _get_simulated_data(self, sensor_type: Optional[str], node_id: Optional[str], limit: int) -> List[Dict]:
        """Return simulated data when InfluxDB is not available"""
        import random
        from datetime import datetime, timezone
        
        sensor_types = [sensor_type] if sensor_type else ["temperature", "air_humidity", "soil_moisture", "luminosity"]
        nodes = [node_id] if node_id else ["node_01", "node_02", "robot_01"]
        
        readings = []
        for i in range(min(limit, len(sensor_types) * len(nodes))):
            st = sensor_types[i % len(sensor_types)]
            nd = nodes[i % len(nodes)]
            
            # Simulated values
            if st == "temperature":
                value = round(random.uniform(18.0, 32.0), 2)
            elif st == "air_humidity":
                value = round(random.uniform(40.0, 85.0), 2)
            elif st == "soil_moisture":
                value = round(random.uniform(25.0, 75.0), 2)
            else:  # luminosity
                value = round(random.uniform(1000, 50000), 0)
            
            readings.append({
                "node_id": nd,
                "sensor_type": st,
                "value": value,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return readings
    
    def _get_simulated_historical_data(self, sensor_type: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Return simulated historical data"""
        import random
        from datetime import timedelta
        
        data_points = []
        current_time = start_time
        interval = timedelta(minutes=5)
        
        while current_time <= end_time:
            if sensor_type == "temperature":
                value = round(random.uniform(18.0, 32.0), 2)
            elif sensor_type == "air_humidity":
                value = round(random.uniform(40.0, 85.0), 2)
            elif sensor_type == "soil_moisture":
                value = round(random.uniform(25.0, 75.0), 2)
            else:  # luminosity
                value = round(random.uniform(1000, 50000), 0)
            
            data_points.append({
                "timestamp": current_time.isoformat(),
                "value": value,
                "node_id": "node_01"
            })
            
            current_time += interval
        
        return data_points

influx_manager = InfluxDBManager()