# Endpoints adicionales para gestión de usuarios

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone
from auth import get_current_admin_user, get_password_hash
from database import Database
from config import SQLITE_DB
from models import UserInToken

user_router = APIRouter(prefix="/api/admin")
db = Database(SQLITE_DB)

@user_router.get("/users")
async def get_all_users(current_user: UserInToken = Depends(get_current_admin_user)):
    """Get all users (admin only)"""
    import aiosqlite
    
    async with aiosqlite.connect(db.db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT id, username, email, full_name, role, created_at, is_active FROM users ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        
        # Get simulation mode for each user
        users = []
        for row in rows:
            user_dict = dict(row)
            # Check if user has individual simulation mode in config
            user_dict['simulation_mode'] = False  # Default
            users.append(user_dict)
        
        return users

@user_router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    user_data: dict,
    current_user: UserInToken = Depends(get_current_admin_user)
):
    """Create new user and send welcome email (admin only)"""
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'full_name']
    for field in required_fields:
        if field not in user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    # Check if user exists
    existing_user = await db.get_user_by_username(user_data['username'])
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    existing_email = await db.get_user_by_email(user_data['email'])
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data['password'])
    
    # Create user
    user_id = await db.create_user(
        user_data['username'],
        user_data['email'],
        hashed_password,
        user_data['full_name'],
        user_data.get('role', 'agricultor')
    )
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # TODO: Send welcome email
    # send_welcome_email(user_data['email'], user_data['username'], user_data['password'])
    
    return {
        "status": "success",
        "message": "Usuario creado exitosamente",
        "user_id": user_id
    }

@user_router.patch("/users/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    data: dict,
    current_user: UserInToken = Depends(get_current_admin_user)
):
    """Activate/deactivate user (admin only)"""
    import aiosqlite
    
    async with aiosqlite.connect(db.db_path) as conn:
        await conn.execute(
            "UPDATE users SET is_active = ? WHERE id = ?",
            (data['is_active'], user_id)
        )
        await conn.commit()
    
    return {"status": "success", "message": "User status updated"}

@user_router.patch("/users/{user_id}/simulation")
async def toggle_user_simulation(
    user_id: int,
    data: dict,
    current_user: UserInToken = Depends(get_current_admin_user)
):
    """Toggle simulation mode for user (admin only)"""
    import json
    from pathlib import Path
    
    config_file = Path(__file__).parent / "config_admin.json"
    
    # Load existing config
    config = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    
    # Update user simulation modes
    if 'user_simulations' not in config:
        config['user_simulations'] = {}
    
    config['user_simulations'][str(user_id)] = data['simulation_mode']
    
    # Save
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    return {"status": "success", "message": "Simulation mode updated"}

@user_router.patch("/users/{user_id}/password")
async def change_user_password(
    user_id: int,
    data: dict,
    current_user: UserInToken = Depends(get_current_admin_user)
):
    """Change user password (admin only)"""
    import aiosqlite
    
    if 'new_password' not in data or len(data['new_password']) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    hashed_password = get_password_hash(data['new_password'])
    
    async with aiosqlite.connect(db.db_path) as conn:
        await conn.execute(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            (hashed_password, user_id)
        )
        await conn.commit()
    
    # TODO: Send notification email
    
    return {"status": "success", "message": "Password updated"}

@user_router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserInToken = Depends(get_current_admin_user)
):
    """Delete user (admin only)"""
    import aiosqlite
    
    # Prevent deleting admin users
    async with aiosqlite.connect(db.db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user = await cursor.fetchone()
        
        if user and user['role'] == 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete admin users"
            )
        
        await conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await conn.commit()
    
    return {"status": "success", "message": "User deleted"}

import aiosqlite
