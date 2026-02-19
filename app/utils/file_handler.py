import aiofiles
from uuid import uuid4
from app.config import settings

async def save_temp_file(upload_file):
    path = settings.UPLOAD_TEMP_DIR / f"{uuid4()}_{upload_file.filename}"
    async with aiofiles.open(path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return path