from fastapi import Depends, HTTPException, Header
import app.database as database

async def get_db():
    if database.db is None:
        raise HTTPException(500, "DB not ready")
    return database.db

async def get_current_user_id(x_user_id: str = Header(..., description="User ID for tracking uploads")):
    """Extract user_id from request header. For production, replace with JWT auth."""
    if not x_user_id or len(x_user_id.strip()) == 0:
        raise HTTPException(400, "X-User-ID header required")
    return x_user_id.strip()