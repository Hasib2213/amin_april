from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    await client.admin.command('ping')
    print("MongoDB connected")

async def close_db():
    if client:
        client.close()
        print("MongoDB closed")