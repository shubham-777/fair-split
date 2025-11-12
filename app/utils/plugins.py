from redis import Redis

from app.config import settings
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

redis_client = Redis(host=settings.REDIS_HOST,
                     port=settings.REDIS_PORT,
                     db=settings.REDIS_DB,
                     decode_responses=True)
