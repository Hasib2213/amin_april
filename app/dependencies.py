from fastapi import Depends, HTTPException
import app.database as database

async def get_db():
    if database.db is None:
        raise HTTPException(500, "DB not ready")
    return database.db