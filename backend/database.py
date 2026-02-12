import aiosqlite
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        
    async def init_db(self):
        """Initialize the database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT DEFAULT 'agricultor',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Alerts table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    sensor_id TEXT,
                    value REAL,
                    threshold REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged INTEGER DEFAULT 0,
                    acknowledged_by INTEGER,
                    acknowledged_at TIMESTAMP,
                    FOREIGN KEY (acknowledged_by) REFERENCES users(id)
                )
            """)
            
            # Robot commands history
            await db.execute("""
                CREATE TABLE IF NOT EXISTS robot_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    command_type TEXT NOT NULL,
                    command_data TEXT,
                    status TEXT DEFAULT 'sent',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            await db.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    async def create_user(self, username: str, email: str, hashed_password: str, 
                         full_name: str, role: str = 'agricultor') -> Optional[int]:
        """Create a new user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "INSERT INTO users (username, email, hashed_password, full_name, role) VALUES (?, ?, ?, ?, ?)",
                    (username, email, hashed_password, full_name, role)
                )
                await db.commit()
                return cursor.lastrowid
        except aiosqlite.IntegrityError:
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE email = ? AND is_active = 1",
                (email,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def create_alert(self, alert_type: str, severity: str, message: str,
                          sensor_id: str = None, value: float = None, 
                          threshold: float = None) -> int:
        """Create a new alert"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO alerts (alert_type, severity, message, sensor_id, value, threshold)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (alert_type, severity, message, sensor_id, value, threshold)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_alerts(self, limit: int = 50, acknowledged: bool = None) -> List[Dict]:
        """Get alerts"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = "SELECT * FROM alerts"
            params = []
            
            if acknowledged is not None:
                query += " WHERE acknowledged = ?"
                params.append(1 if acknowledged else 0)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def acknowledge_alert(self, alert_id: int, user_id: int) -> bool:
        """Acknowledge an alert"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE alerts SET acknowledged = 1, acknowledged_by = ?, acknowledged_at = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id, alert_id)
            )
            await db.commit()
            return True
    
    async def create_robot_command(self, user_id: int, command_type: str, 
                                  command_data: str = None) -> int:
        """Log robot command"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO robot_commands (user_id, command_type, command_data) VALUES (?, ?, ?)",
                (user_id, command_type, command_data)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_robot_commands(self, limit: int = 50) -> List[Dict]:
        """Get robot command history"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM robot_commands ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]